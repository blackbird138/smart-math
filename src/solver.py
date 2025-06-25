import json
from pathlib import Path
from textwrap import dedent
from typing import List, Dict, Optional
import re
import yaml

from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.messages import BaseMessage
from camel.toolkits import FunctionTool
from camel.types import ModelPlatformType

from src.datamodel import ParagraphChunk
from src.rag.retriever import RetrieverManager

BASE_DIR = Path(__file__).resolve().parent.parent

with open(BASE_DIR / "config" / "agent_config.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)["GENERATE_MODEL"]

platform = cfg.get("model_platform", "SILICONFLOW")
try:
    _model = ModelFactory.create(
        model_platform=ModelPlatformType[platform],
        model_type=cfg.get("model_type", "Pro/deepseek-ai/DeepSeek-R1"),
        model_config_dict=cfg.get("model_config", None),
    )
except Exception:
    _model = ModelFactory.create(
        model_platform=ModelPlatformType.DEFAULT,
        model_type="stub",
    )

_system_msg = BaseMessage.make_assistant_message(
    role_name="math_solver",
    content=dedent(
        """
        你是一个数学题解助手，可以调用工具 `search_chunks` 查询相关词条（如定理，命题，定义等）。
        当在证明中引用某个词条时，请使用格式 [REF:{chunk_type}/{chunk_number}/{chunk_summary}] 标注。
        在获得足够信息后给出完整的解答和证明。
        
        有如下几个要求：
        1. 输出使用 markdown 可直接渲染解析的格式，LaTeX 公式要放在 $$ 中。
        2. 尽量使用 `search_chunks` 可查询到的词条解决问题。
        """
    ),
)


class MathSolver:
    def __init__(self, retriever: Optional[RetrieverManager], docs: List[ParagraphChunk]):
        self.retriever = retriever
        self.docs = docs
        self.tool = FunctionTool(self.search_chunks)
        self.agent = ChatAgent(
            system_message=_system_msg,
            model=_model,
            output_language="中文",
            tools=[self.tool],
        )

    def search_chunks(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        """搜索与查询相关的 chunk 内容。"""
        hits = []
        print(f"<UNK> {query} <UNK>")
        if self.retriever is not None:
            try:
                hits = self.retriever.retrieve(query, top_k=top_k)
            except Exception:
                hits = []
        if not hits:
            # 简单回退：在本地 docs 中按关键字搜索
            for c in self.docs:
                if query in c.page_content:
                    hits.append({"text": c.page_content, "metadata": c.metadata})
                    if len(hits) >= top_k:
                        break
        results = []
        for h in hits:
            md = h.get("metadata", {})
            results.append({
                "chunk_id": md.get("chunk_id", ""),
                "chunk_type": md.get("chunk_type", ""),
                "chunk_number": md.get("number", ""),
                "chunk_summary": md.get("summary", ""),
                "content": h.get("text", ""),
            })
        return results


    def _validate_refs(self, text: str) -> str:
        """校验回答中的引用是否存在，不存在的标注为无效引用."""
        pattern = re.compile(r"\[REF:([^/]+)/([^/]+)/([^\]]*)\]")

        def repl(match: re.Match) -> str:
            chunk_type, num, summary = match.groups()
            query = f"{chunk_type} {num} {summary}".strip()
            res = self.search_chunks(query, top_k=1)
            if res:
                return match.group(0)
            return f"[无效引用:{chunk_type}/{num}]"

        return pattern.sub(repl, text)

    def solve(self, question: str) -> str:
        """让模型自行调用 ``search_chunks`` 完成检索，并在返回结果后校验引用."""
        user_msg = BaseMessage.make_user_message("user", question)
        rsp = self.agent.step(user_msg)
        answer = rsp.msgs[0].content
        return self._validate_refs(answer)
