# src/graph/pair_reranker.py

import os
from src.graph.siliconflow_reranker import SiliconflowReranker

class PairReranker:
    def __init__(self, batch_size=16):
        self.remote = SiliconflowReranker()
        self.batch = batch_size

    def score_pairs(self, pairs):
        # 可按 batch_size 切分后调 remote.embed_list
        scores = []
        for i in range(0, len(pairs), self.batch):
            scores.extend(self.remote.embed_list(pairs[i:i+self.batch]))
        return scores
