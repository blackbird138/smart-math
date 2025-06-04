# src/rag/retriever.py

from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

from qdrant_client import QdrantClient, models
from camel.retrievers.vector_retriever import VectorRetriever
from src.rag.embedding import EmbeddingManager


@dataclass
class RetrievedDoc:
    doc_id: str
    score: float
    source: str
    payload: dict

class DenseRetriever:
    def __init__(self, client: QdrantClient, collection: str, embedder: EmbeddingManager):
        self.c = client
        self.col = collection
        self.embedder = embedder

    def search(self, query: str, top_k: int = 20) -> List[RetrievedDoc]:
        qv = self.embedder.embed(query)
        hits = self.c.search(
            self.col,
            query_vector=("dense", qv),
            limit=top_k,
            with_vectors=False,
            with_payload=True
        )   # Qdrant dense search
        return [RetrievedDoc(str(p.id), p.score, "dense", p.payload) for p in hits]



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

    def topk_pairs(self, ids: list[str]) -> set[tuple[str,str,float]]:
        pairs = set()
        for pid in ids:
            res = self.store.client.search(
                collection_name="smart_math",
                query_vector={"id": pid},
                limit=self.top_k,
                with_payload=False,
            )
            for hit in res:
                if hit.id == pid or hit.score < self.threshold:
                    continue
                pair = tuple(sorted([pid, hit.id]))
                pairs.add((*pair, hit.score))
        return pairs
