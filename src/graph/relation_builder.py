# src/graph/relation_builder.py

import json, os, time, backoff
from typing import List, Dict
from textwrap import dedent
from jsonschema import validate, ValidationError
from dotenv import load_dotenv
from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from camel.messages import BaseMessage
from camel.utils.commons import BatchProcessor
from itertools import islice
from src.datamodel import ParagraphChunk

load_dotenv()

class SizeMismatchError(Exception):
    pass

REL_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["related", "relation_type", "summary"],
        "properties": {
            "related": {"type": "boolean"},
            "relation_type": {"type": "string"},
            "summary": {"type": "string"},
        },
    },
}

sys_msg = BaseMessage.make_assistant_message(
    role_name="math_editor",
    content=dedent(
        """
        你是一名严谨的数学编辑。
        输入：若干对<b>数学文本</b>（都是定理/引理/命题），假设一对数学文本分别为 text1 和 text2 则按照以下格式给出：
            [<id>] <text1_type>:<text1>\n<text2_type>:<text2>
        
        任务：
        输出一个 JSON 列表，列表的每个元素由对一对数学文本依次进行如下操作得到：
        1. 判断数学文本 text1 和 text2 是否存在直接或隐含的数学关系。
        2. 如果存在数学关系：
           a. 将 text2 之于 text1 的数学关系名称填入 `relation_type` 字段（如: 推论/特例/同构/补充/等价）。
           b. 用一句话简述二者之间的数学关系，并填入 `summary` 字段，使用 markdown 格式。
           c. 将 `related` 字段置为 true。
        3. 如果判断为假：
           a. 将 `related` 字段置为 false。
           b. 将 `relation_type` 字段和 `summary` 字段设为空字符串。
        4. 最终输出一个 JSON 列表。
        """
    )
)

batcher = BatchProcessor(initial_batch_size=50, max_workers=4)

def _iter_batches(iterable):
    it = iter(iterable)
    while (chunk := list(islice(it, batcher.batch_size))):
        yield chunk

def _make_user_prompt(pairs, chunks):
    """把一个 batch 的候选对拼成 user prompt"""
    lines = []
    for idx, (h, t, _) in enumerate(pairs, 1):
        lines.append(f"[{idx}] {chunks[h].metadata['chunk_type']}:{chunks[h].page_content[:250]}\n{chunks[t].metadata['chunk_type']}:{chunks[t].page_content[:250]}")
    return "\n\n".join(lines)

class RelationBuilder:
    def __init__(self, config: dict, batch_size=10):
        self.batch = batch_size

        model_config = config["model_config"]

        model_config["response_format"]={
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

        self.agent = ChatAgent(
            system_message=sys_msg,
            model=self.model,
            output_language="中文",
        )

    @backoff.on_exception(backoff.expo, Exception, max_tries=5)
    def _call_llm(self, user_msg):
        return self.agent.step(user_msg).msgs[0].content

    def build_relations(self, chunks: Dict[str, ParagraphChunk], candidate_pairs):
        triples = []
        for pair_batch in _iter_batches(candidate_pairs):
            t0 = time.time()
            user_msg = BaseMessage.make_user_message(
                role_name="pairs_provider",
                content="\n\n输入数据：\n" + _make_user_prompt(pair_batch, chunks)
            )
            rsp = self._call_llm(user_msg)
            try:
                data = json.loads(rsp)
                validate(data, REL_SCHEMA)
                if len(data) != len(pair_batch):
                    raise SizeMismatchError(
                        f"解析的数据条数 ({len(data)}) 与输入的对数 ({len(pair_batch)}) 不一致"
                    )
            except (json.JSONDecodeError, ValidationError):
                print("Schema 校验失败")
            except SizeMismatchError as e:
                print(f"错误: {e}")
            for (pair, res) in zip(pair_batch, data):
                if res["related"] == True:
                    triples.append({
                        "head": pair[0],
                        "tail": pair[1],
                        "relation_type": res["relation_type"],
                        "summary": res["summary"],
                    })
            batcher.adjust_batch_size(success=True, processing_time=time.time() - t0)
        return triples
