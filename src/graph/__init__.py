from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Set, Tuple

from src.datamodel import ParagraphChunk
from src.rag.retriever import RetrieverManager
from .relation_builder import RelationBuilder
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GraphBuilder:
    """构建并保存数学文本之间的关系图."""

    def __init__(self, retriever: RetrieverManager,
                 relation_builder: RelationBuilder, file_id: str, top_k: int = 5,
                 base_dir: str = "data") -> None:
        self.retriever = retriever
        self.relation_builder = relation_builder
        self.top_k = top_k
        self.base_dir = Path(base_dir)
        self.file_id = file_id
        logger.info("GraphBuilder initialized for %s", file_id)

    def _build_pairs(self, chunks: List[ParagraphChunk]) -> List[tuple[str, str, float]]:
        logger.info("Building candidate pairs")
        pairs = list(self.retriever.topk_pairs(chunks))
        if not pairs:
            return []

        logger.info("Built %d pairs", len(pairs))
        return pairs

    def build_relations(self, chunks: List[ParagraphChunk]) -> List[dict]:
        if not chunks:
            return []
        chunk_dics: Dict[str, ParagraphChunk] = {}
        for c in chunks:
            chunk_dics[c.id] = c

        candidate_pairs = self._build_pairs(chunks)
        if not candidate_pairs:
            return []
        relations = self.relation_builder.build_relations(chunk_dics, candidate_pairs)
        relations = self._deduplicate_relations(relations)
        logger.info("Built %d relations", len(relations))
        return relations

    def _deduplicate_relations(self, relations: List[dict]) -> List[dict]:
        """移除重复的关系对，只保留唯一的 (head, tail, relation_type)"""
        seen: Set[Tuple[str, str, str]] = set()
        unique = []
        for r in relations:
            key = (r.get("head"), r.get("tail"), r.get("relation_type", ""))
            if key not in seen:
                seen.add(key)
                unique.append(r)
        return unique

    def save_relations(self, relations: List[dict]) -> None:
        target_dir = self.base_dir / self.file_id
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / "relations.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(relations, f, ensure_ascii=False, indent=2)
        logger.info("Relations saved to %s", path)

    def build_and_save(self, chunks: List[ParagraphChunk]) -> List[dict]:
        relations = self.build_relations(chunks)
        if relations:
            self.save_relations(relations)
        return relations
