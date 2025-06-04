# src/graph/siliconflow_reranker.py
"""A lightweight placeholder for the real Siliconflow reranker service."""

from typing import List


class SiliconflowReranker:
    """Dummy implementation returning zero scores for each pair."""

    def embed_list(self, pairs: List[str]) -> List[float]:
        return [0.0 for _ in pairs]
