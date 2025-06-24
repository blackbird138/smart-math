# src/rag/retriever.py

from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

from qdrant_client import QdrantClient, models
from camel.retrievers.vector_retriever import VectorRetriever
from src.rag.embedding import EmbeddingManager
from src.datamodel import ParagraphChunk

@dataclass
class RetrievedDoc:
    doc_id: str
    score: float
    source: str
    payload: dict

class RetrieverManager:
    def __init__(self, embedding_mgr: EmbeddingManager, config: dict):
        self.emb_mgr = embedding_mgr
        self.store = self.emb_mgr.storage
        self.retriever = VectorRetriever(
            embedding_model=self.emb_mgr.embedder,
            storage=self.store
        )
        self.top_k = config.get("top_k", 5)
        self.threshold = config.get("threshold", 0.4)

    def retrieve(self, query: str, top_k: int = None) -> list[dict]:
        """
        对 query 进行检索，返回 top_k 相关文档片段列表。
        """
        k = top_k or self.top_k
        hits = self.retriever.query(query, top_k=k, similarity_threshold = 0.1)
        # 转换输出格式
        return hits

    def topk_pairs(self, chunks: List[ParagraphChunk]) -> set[tuple[str,str,float]]:
        pairs = set()
        for chunk in chunks:
            res = self.retriever.query(chunk.page_content, top_k=self.top_k, similarity_threshold = 0.1)
            for hit in res:
                if hit["metadata"]["chunk_id"] == chunk.metadata["chunk_id"]:
                    continue
                pair = tuple(sorted([chunk.metadata["chunk_id"], hit["metadata"]["chunk_id"]]))
                pairs.add((*pair, hit["similarity score"]))
        return pairs
