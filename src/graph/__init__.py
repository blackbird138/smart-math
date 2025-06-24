from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict

from src.datamodel import ParagraphChunk
from src.rag.retriever import RetrieverManager
from .pair_reranker import PairReranker
from .relation_builder import RelationBuilder


class GraphBuilder:
    """构建并保存数学文本之间的关系图."""

    def __init__(self, retriever: RetrieverManager, reranker: PairReranker,
                 relation_builder: RelationBuilder, top_k: int = 5,
                 base_dir: str = "data") -> None:
        self.retriever = retriever
        self.reranker = reranker
        self.relation_builder = relation_builder
        self.top_k = top_k
        self.base_dir = Path(base_dir)

    def _build_pairs(self, file_id: str, chunks: List[ParagraphChunk]) -> List[tuple[str, str, float]]:
        ids = [c.id for c in chunks]
        pairs = list(self.retriever.topk_pairs(file_id, ids))
        if not pairs:
            return []

        # 使用摘要文本进行 rerank
        summaries: Dict[str, str] = {}
        for c in chunks:
            summaries[c.id] = c.metadata.get("summary", c.page_content if isinstance(c.page_content, str) else "\n".join(c.page_content))

        pair_inputs = [f"{summaries[h]}\n{summaries[t]}" for h, t, _ in pairs]
        scores = self.reranker.score_pairs(pair_inputs)
        ranked = sorted(zip(pairs, scores), key=lambda x: x[1], reverse=True)
        return [(h, t, s) for (h, t, _), s in ranked[: self.top_k]]

    def build_relations(self, file_id: str, chunks: List[ParagraphChunk]) -> List[dict]:
        if not chunks:
            return []
        chunk_texts: Dict[str, str] = {}
        for c in chunks:
            text = c.page_content if isinstance(c.page_content, str) else "\n".join(c.page_content)
            chunk_texts[c.id] = text

        candidate_pairs = self._build_pairs(file_id, chunks)
        if not candidate_pairs:
            return []
        return self.relation_builder.build_relations(chunk_texts, candidate_pairs)

    def save_relations(self, file_id: str, relations: List[dict]) -> None:
        target_dir = self.base_dir / file_id
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / "relations.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(relations, f, ensure_ascii=False, indent=2)

    def build_and_save(self, file_id: str, chunks: List[ParagraphChunk]) -> List[dict]:
        relations = self.build_relations(file_id, chunks)
        if relations:
            new_file_id = chunks[0].metadata.get("file_id", "default")
            self.save_relations(new_file_id, relations)
        return relations
