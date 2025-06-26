from src.graph.pair_reranker import PairReranker


def test_score_pairs_varies(monkeypatch):
    monkeypatch.setenv("SILICONFLOW_API_KEY", "dummy")

    def fake_rerank(self, query, documents):
        return [1.0 if query == documents[0] else 0.5]

    monkeypatch.setattr(
        "src.graph.siliconflow_reranker.SiliconflowReranker.rerank", fake_rerank
    )

    r = PairReranker(batch_size=2)
    pairs = [
        "theorem A\ntheorem A",
        "theorem A\nlemma B",
    ]
    scores = r.score_pairs(pairs)
    assert len(scores) == 2
    assert scores[0] > scores[1]
