import json
from pathlib import Path
from textwrap import dedent
from typing import List, Dict, Optional
import re
import yaml

from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.messages import BaseMessage
from camel.types import ModelPlatformType, RoleType

from src.utils.logger import get_logger

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
        你是一个数学题解助手。用户的问题前会附带与主题相关的词条（定理、命题、定义等）。
        请充分利用这些词条完成证明和解答，引用时使用格式 [REF:{chunk_id}]，其中 chunk_id 已在题目中给出。

        有如下要求：
        1. 输出使用 markdown 可直接渲染解析的格式，LaTeX 公式要放在 $$ 中。
        2. 仅可引用用户提供的词条，不要编造文档库中不存在的引用。
        """
    ),
)

logger = get_logger(__name__)


class ConversationMemory:
    """维护最近若干轮对话的简单记忆."""

    def __init__(self, max_rounds: int = 3) -> None:
        self.max_rounds = max_rounds
        self.history: List[BaseMessage] = []

    def add(self, role: str, content: str) -> None:
        if role == "user":
            msg = BaseMessage.make_user_message("user", content)
        else:
            msg = BaseMessage.make_assistant_message("assistant", content)
        self.history.append(msg)
        limit = self.max_rounds * 2
        if len(self.history) > limit:
            self.history = self.history[-limit:]

    def to_messages(self) -> List[Dict]:
        msgs: List[Dict] = []
        for m in self.history:
            if m.role_type == RoleType.USER:
                msgs.append(m.to_openai_user_message())
            else:
                msgs.append(m.to_openai_assistant_message())
        return msgs

    def clear(self) -> None:
        self.history.clear()


class MathSolver:
    def __init__(
        self,
        retriever: Optional[RetrieverManager],
        docs: List[ParagraphChunk],
        memory: Optional[ConversationMemory] = None,
    ) -> None:
        self.retriever = retriever
        self.docs = docs
        self.docs_dict = {}
        for doc in self.docs:
            self.docs_dict[doc.id] = doc
        self.agent = ChatAgent(
            system_message=_system_msg,
            model=_model,
            output_language="中文",
        )
        self.memory = memory or ConversationMemory()
        logger.info("MathSolver initialized with %d docs", len(self.docs))

    def search_chunks(self, query: str, top_k: int = 10) -> List[str]:
        r"""查询文档库里相关的词条（定理/命题/定义 等）。"""
        logger.info("Searching chunks for query: %s", query)
        hits = []
        if self.retriever is not None:
            try:
                hits = self.retriever.retrieve(query, top_k=top_k)
            except Exception as e:
                logger.error("Retrieve failed: %s", e)
                hits = []
        if not hits:
            return []
        ids: List[str] = []
        for h in hits:
            md = h.get("metadata", {})
            cid = md.get("chunk_id")
            if cid:
                ids.append(cid)
        logger.info("Retrieved %d related chunks", len(ids))
        return ids

    def _validate_refs(self, text: str) -> str:
        """校验回答中的引用是否存在，不存在的标注为无效引用."""
        pattern = re.compile(r"\[REF:([^\]\n]+)\]")

        def repl(match: re.Match) -> str:
            chunk_id = match.group(1).strip()
            if chunk_id in self.docs_dict:
                return match.group(0)
            return ""

        return pattern.sub(repl, text)

    def solve(self, question: str) -> str:
        """结合检索结果与历史对话回答问题并校验引用."""
        logger.info("Solving question via LLM")
        chunk_ids = self.search_chunks(question, top_k=10)
        context_parts = []
        for idx, cid in enumerate(chunk_ids, 1):
            doc = self.docs_dict.get(cid)
            if not doc:
                continue
            content = doc.page_content
            if isinstance(content, list):
                content = " ".join(content)
            context_parts.append(f"{idx}. {content} [REF:{cid}]")

        prompt = question
        if context_parts:
            prompt += "\n\n以下词条供参考，请在需要时引用：\n" + "\n".join(
                context_parts
            )

        messages = [_system_msg.to_openai_assistant_message()]
        messages.extend(self.memory.to_messages())
        messages.append({"role": "user", "content": prompt})

        req_cfg = _model.model_config_dict.copy()
        req_cfg.pop("stream", None)

        rsp = _model._client.chat.completions.create(
            messages=messages, model=_model.model_type, **req_cfg
        )
        answer = self._validate_refs(rsp.choices[0].message.content)
        self.memory.add("user", question)
        self.memory.add("assistant", answer)
        logger.info("LLM answered: %s", answer)
        return answer

    def stream_solve(self, question: str):
        """以流式方式返回解答过程, 会利用历史对话."""
        logger.info("Streaming solution via LLM")
        chunk_ids = self.search_chunks(question, top_k=10)
        context_parts = []
        for idx, cid in enumerate(chunk_ids, 1):
            doc = self.docs_dict.get(cid)
            if not doc:
                continue
            content = doc.page_content
            if isinstance(content, list):
                content = " ".join(content)
            context_parts.append(f"{idx}. {content} [REF:{cid}]")

        prompt = question
        if context_parts:
            prompt += "\n\n以下词条供参考，请在需要时引用：\n" + "\n".join(
                context_parts
            )

        messages = [_system_msg.to_openai_assistant_message()]
        messages.extend(self.memory.to_messages())
        messages.append({"role": "user", "content": prompt})

        req_cfg = _model.model_config_dict.copy()
        req_cfg["stream"] = True

        stream = _model._client.chat.completions.create(
            messages=messages, model=_model.model_type, **req_cfg
        )

        acc = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                acc += delta
                yield delta

        final = self._validate_refs(acc)
        if final != acc:
            yield "\n" + final
        self.memory.add("user", question)
        self.memory.add("assistant", final)
        logger.info("LLM streaming completed")
