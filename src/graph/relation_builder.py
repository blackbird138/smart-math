# src/graph/relation_builder.py

import json, backoff
from typing import Dict
from textwrap import dedent
from jsonschema import validate, ValidationError
from dotenv import load_dotenv
from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from camel.messages import BaseMessage

from src.datamodel import ParagraphChunk

load_dotenv()


REL_SCHEMA = {
    "type": "object",
    "required": ["head", "tail", "related", "relation_type", "summary"],
    "properties": {
        "head": {"type": "string"},
        "tail": {"type": "string"},
        "related": {"type": "boolean"},
        "relation_type": {"type": "string"},
        "summary": {"type": "string"},
    },
}

sys_msg = BaseMessage.make_assistant_message(
    role_name="math_editor",
    content=dedent(
        """
        你是一名严谨的数学编辑。
        输入：一对<b>数学文本</b>（都是定理/引理/命题），假设两段文本分别为 text1 和 text2，格式如下：
            <text1_type>:<text1>\n<text2_type>:<text2>

        任务：
        输出一个 JSON 对象，按以下步骤处理这对数学文本：
        1. 将 text1_type 填入 `head` 字段，将 text2_type 填入 `tail` 字段。
        2. 判断数学文本 text1 和 text2 是否存在直接或隐含的数学关系。
        3. 如果存在数学关系：
           a. 将二者的数学关系名称填入 `relation_type` 字段（如: 推论/特例/同构/补充/等价）。
           b. 用一句话简述二者之间的数学关系，并填入 `summary` 字段，使用 markdown 格式。
           c. 将 `related` 字段置为 true。
        4. 如果判断为假：
           a. 将 `related` 字段置为 false。
           b. 将 `relation_type` 字段和 `summary` 字段设为空字符串。
        5. 最终输出一个 JSON 对象。
        """
    )
)

def _make_user_prompt(pair, chunks):
    """构造单个候选对的用户提示"""
    h, t, _ = pair
    return (
        f"{chunks[h].metadata['chunk_type']}:{chunks[h].metadata['summary']}\n"
        f"{chunks[t].metadata['chunk_type']}:{chunks[t].metadata['summary']}"
    )


class RelationBuilder:
    def __init__(self, config: dict, batch_size=10):
        self.batch = batch_size

        model_config = config["model_config"]

        model_config["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "MathEditResult",
                "schema": REL_SCHEMA
            }
        }

        self.model = ModelFactory.create(
            model_platform=ModelPlatformType[config["model_platform"]],
            model_type=config["model_type"],
            model_config_dict=model_config,
        )

    @backoff.on_exception(backoff.expo, Exception, max_tries=5)
    def _call_llm(self, user_msg):
        agent = ChatAgent(
            system_message=sys_msg,
            model=self.model,
            output_language="中文",
        )
        return agent.step(user_msg).msgs[0].content

    def build_relations(self, chunks: Dict[str, ParagraphChunk], candidate_pairs):
        """逐个调用 LLM 构建关系"""
        triples = []
        for pair in candidate_pairs:
            user_msg = BaseMessage.make_user_message(
                role_name="pairs_provider",
                content="\n\n输入数据：\n" + _make_user_prompt(pair, chunks)
            )
            rsp = self._call_llm(user_msg)
            try:
                data = json.loads(rsp)
                validate(data, REL_SCHEMA)
            except (json.JSONDecodeError, ValidationError):
                print("Schema 校验失败")
                continue

            if data.get("related"):
                triples.append({
                    "head": pair[0],
                    "tail": pair[1],
                    "relation_type": data.get("relation_type", ""),
                    "summary": data.get("summary", ""),
                })
        return triples