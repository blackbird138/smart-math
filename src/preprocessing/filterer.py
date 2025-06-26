# src/preprocessing/filterer.py

import json, yaml, tiktoken, backoff
import re
from dotenv import load_dotenv
from pathlib import Path
from textwrap import dedent
from typing import List, Dict, Any
from pydantic import BaseModel, ValidationError, RootModel
from jsonschema import validate
from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType, OpenAIBackendRole
from camel.messages import BaseMessage
from src.datamodel import ParagraphChunk
from src.preprocessing.chunker import chunk_documents, detect_header_type

load_dotenv()

# 1. 从配置文件加载 Agent 配置与 Schema 路径
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # 回到 project_root/
CONFIG_DIR = BASE_DIR / "config"

# 加载 agent 配置
with open(CONFIG_DIR / "agent_config.yaml", "r", encoding="utf-8") as f:
    agent_cfg = yaml.safe_load(f)["PROCESS_MODEL"]

# 2. 定义 Pydantic 模型
FILTER_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["state_code", "content", "summary", "number"],
        "properties": {
            "state_code": {"type": "string"},
            "content": {"type": "string"},
            "summary": {"type": "string"},
            "number": {"type": "string"},
        },
    },
}

# 3. 构造系统消息（包含 Schema）
sys_msg = BaseMessage.make_assistant_message(
    role_name="filterer",
    content=dedent(
        """
        你是一个数学文档处理助手。
        输入：一个 JSON 格式的 chunk 列表，每个 chunk 都包含：
          - chunk_type: 指定的类型（definition/theorem/lemma/exercise等）
          - page_content: 一个 List，包含以段落划分原始文本内容，可能有缺失或多余的内容，多余的内容一定是 List 的一个后缀。

        任务：
        对列表中的每个 chunk 按照输入顺序依次执行以下操作：
        1. 判断 page_content 中一个前缀的内容是否与 chunk_type 指定的类型相符（例如 chunk_type="theorem" 时，判断其是否真的是定理类型内容）。
        2. 如果判断为真，且 page_content 没有缺失的内容：
           a. 将 `content` 置为符合要求的那个 page_content 的前缀，一定要保证内容的完整，只要前后两段后段是前端的补充说明就要放在一起。
           b. 讲 `summary` 置为该 chunk 内容的一句话（一个短词）总结。
           c. 将 `state_code` 置为 "001"。
           d. 若 chunk 标题中包含编号（如 "定理 4.1.3"），提取编号（如 "4.1.3"）填入 `number` 字段；否则 `number` 置为空字符串。
        3. 如果判断为真，但 page_content 有缺失的内容，如以“以下”，“如下”作为结尾：
           a. 将 `content` 和 `summary` 置为空字符串。
           b. 将 `state_code` 置为 "002"。
        4. 如果判断为假：
           a. 将 `content` 和 `summary` 置为空字符串。
           b. 将 `state_code` 置为 "003"。
        最终输出一个 JSON 列表。
        """
    ),
)

# 4. 初始化 ChatAgent
enc = tiktoken.get_encoding("cl100k_base")
CTX_LIMIT = agent_cfg["model_config"]["max_tokens"]  # 模型上下文
SAFETY = 1024  # 给输出留余量

response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "ChunkFilterResults",
        "schema": FILTER_SCHEMA,
    },
}


model = ModelFactory.create(
    model_platform=ModelPlatformType[agent_cfg["model_platform"]],
    model_type=agent_cfg["model_type"],
    model_config_dict=agent_cfg["model_config"],
)

agent = ChatAgent(
    system_message=sys_msg,
    model=model,
    output_language="中文",
)


# 5. 批量过滤与转换函数
def _tok(s: str) -> int:
    return len(enc.encode(s))


def normalize_latex_block(text: str) -> str:
    """确保行间公式 $$...$$ 或 \[...\] 前后带换行"""
    pattern = re.compile(r"(\$\$.*?\$\$|\\\[.*?\\\])", re.DOTALL)

    def repl(match: re.Match) -> str:
        block = match.group(0)
        if block.startswith("$$"):
            inner = block[2:-2].strip()
            return f"\n$$\n{inner}\n$$\n"
        else:
            inner = block[2:-2].strip()
            return f"\n\\[\n{inner}\n\\]\n"

    return pattern.sub(repl, text)


def build_batches(items, limit=CTX_LIMIT - SAFETY):
    cur, cur_tok, out = [], 0, []
    for it in items:
        t = _tok(json.dumps(it, ensure_ascii=False))
        if cur and cur_tok + t > limit:
            out.append(cur)
            cur, cur_tok = [], 0
        cur.append(it)
        cur_tok += t
    if cur:
        out.append(cur)
    return out  # [[dict, ...], [dict, ...], ...]


def llm_call(batch):
    prompt = "\n\n输入数据：\n" + json.dumps(batch, ensure_ascii=False)
    user = BaseMessage.make_user_message("chunk_provider", prompt)

    messages = [
        sys_msg.to_openai_message(OpenAIBackendRole.SYSTEM),
        user.to_openai_message(OpenAIBackendRole.USER),
    ]
    messages = model.preprocess_messages(messages)

    request_cfg = agent_cfg["model_config"].copy()
    request_cfg["response_format"] = response_format
    request_cfg.pop("stream", None)

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def _step():
        rsp = model._client.chat.completions.create(
            messages=messages,
            model=model.model_type,
            **request_cfg,
        )
        return rsp.choices[0].message.content

    return json.loads(_step())  # ⇐ 保证返回 python 对象


def filter_and_convert(chunks: List[ParagraphChunk]) -> (List[ParagraphChunk], List[ParagraphChunk]):
    pure_chunks = []
    for chunk in chunks:
        pure_chunks.append(
            {
                "chunk_type": chunk.metadata["chunk_type"],
                "page_content": chunk.page_content,
            }
        )

    batches = build_batches(pure_chunks)  # 先按 token 切批
    candidate_list = []
    for batch in batches:
        candidate_list.extend(llm_call(batch))

    try:
        validate(candidate_list, FILTER_SCHEMA)
    except ValidationError:
        print("Schema 校验失败")

    results, faild_chunks = [], []
    for item, chunk in zip(candidate_list, chunks):
        if item["state_code"] == "001":
            content = normalize_latex_block(item["content"])
            new_chunk = ParagraphChunk(id=chunk.id, page_content=content, metadata=chunk.metadata)
            new_chunk.metadata["summary"] = item["summary"]
            new_chunk.metadata["number"] = item.get("number", "")
            print("----------------------------------------------")
            print(item)
            print(chunk)
            print(new_chunk)
            results.append(new_chunk)
        elif item["state_code"] == "002":
            faild_chunks.append(ParagraphChunk(id=chunk.id, page_content=chunk.page_content, metadata=chunk.metadata))

    return results, faild_chunks


def chunk_and_filter(docs: List[ParagraphChunk], TOKEN_LIM: int = 500, FAILD_LIM: int = 2000) -> List[ParagraphChunk]:
    chunks = chunk_documents(docs, MAX_TOKEN=TOKEN_LIM)
    docs_dict = {doc.id: (doc, index) for index, doc in enumerate(docs)}

    result, faild_chunks = filter_and_convert(chunks)

    retry_chunks = []
    for chunk in faild_chunks:
        target_chunk, target_index = docs_dict.get(chunk.metadata["initial_id"])
        buf_text = [target_chunk.page_content]
        tok_cnt = len(target_chunk.page_content)
        for next_chunk in docs[target_index + 1 :]:
            if detect_header_type(next_chunk.page_content):
                break
            if tok_cnt > FAILD_LIM:
                break
            buf_text.append(next_chunk.page_content)
            tok_cnt += len(next_chunk.page_content)
        retry_chunks.append(
            ParagraphChunk(id=chunk.id, page_content="\n".join(buf_text).strip(), metadata=chunk.metadata)
        )

    _result, _faild_chunks = filter_and_convert(retry_chunks)

    result.extend(_result)
    return result
