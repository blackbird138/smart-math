# src/graph/pair_reranker.py

from src.graph.siliconflow_reranker import SiliconflowReranker

class PairReranker:
    def __init__(self, batch_size=16):
        self.remote = SiliconflowReranker()
        self.batch = batch_size

    def score_pairs(self, pairs):
        """对文本对进行重排序并返回得分."""
        scores = []
        for pair in pairs:
            if "\n" in pair:
                a, b = pair.split("\n", 1)
            else:
                a, b = pair, ""
            score = self.remote.rerank(a, [b])[0]
            scores.append(score["relevance_score"])

        return scores
