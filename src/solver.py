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
        你是一个数学题解助手，可以调用工具 `search_chunks` 查询文档库中的相关词条（如定理，命题，定义等）。
        当你在证明中使用某个定理/命题，必须通过调用工具 `search_chunks` 查询文档困中是否存在该词条，若存在请使用格式 [REF:{chunk_id}] 标注，其中 chunk_id 可以通过 `search_chunks` 查询的返回值得到。
        在获得足够信息后给出完整的解答和证明。
        
        有如下几个要求：
        1. 输出使用 markdown 可直接渲染解析的格式，LaTeX 公式要放在 $$ 中。
        2. 尽量使用 `search_chunks` 可查询到的词条解决问题。
        3. 不要编造文档库中不存在的词条作为引用。
        """
    ),
)


class MathSolver:
    def __init__(self, retriever: Optional[RetrieverManager], docs: List[ParagraphChunk]):
        self.retriever = retriever
        self.docs = docs
        self.tool = FunctionTool(self.search_chunks)
        self.docs_dict = {}
        for doc in self.docs:
            self.docs_dict[doc.id] = doc
        self.agent = ChatAgent(
            system_message=_system_msg,
            model=_model,
            output_language="中文",
            tools=[self.tool],
        )

    def search_chunks(self, query: str) -> str:
        r"""查询文档库里相关的词条（定理/命题/定义 等）。

        Args:
            query (str): 查询的内容的主题。

        Returns:
            str: 相关词条的 chunk_id
        """
        hits = []
        if self.retriever is not None:
            try:
                hits = self.retriever.retrieve(query, top_k=1)
            except Exception:
                hits = []
        if hits == []:
            return ""
        return hits[0]["metadata"]["chunk_id"]


    def _validate_refs(self, text: str) -> str:
        """校验回答中的引用是否存在，不存在的标注为无效引用."""
        pattern = re.compile(r"\[REF:([^/]+)\]")

        def repl(match: re.Match) -> str:
            chunk_id = match.group(1)
            if chunk_id in self.docs_dict:
                return match.group(0)
            return ""

        return pattern.sub(repl, text)

    def solve(self, question: str) -> str:
        """调用检索工具后向模型提问并校验引用."""

        # 先尝试根据问题检索相关词条，至少调用一次 ``search_chunks``
        chunk_id = self.search_chunks(question)
        context = ""
        if chunk_id and chunk_id in self.docs_dict:
            doc = self.docs_dict[chunk_id]
            # 将检索到的片段内容放入提示中，引导模型正确引用
            context = f"以下内容可能有帮助：\n{doc.page_content}\n[REF:{chunk_id}]\n"

        user_msg = BaseMessage.make_user_message("user", context + question)
        rsp = self.agent.step(user_msg)
        answer = self._validate_refs(rsp.msgs[0].content)
        return answer
