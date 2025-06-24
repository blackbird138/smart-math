import json
from pathlib import Path
from src.graph import GraphBuilder
from src.datamodel import ParagraphChunk

class DummyRetriever:
    def topk_pairs(self, ids):
        return [
            ("a", "b", 0.8),
            ("a", "c", 0.7),
            ("b", "c", 0.6),
        ]

class DummyReranker:
    def __init__(self):
        self.inputs = []
    def score_pairs(self, pairs):
        self.inputs = list(pairs)
        return [0.1, 0.9, 0.2]

class DummyRelationBuilder:
    def __init__(self):
        self.args = None
    def build_relations(self, chunks, pairs):
        self.args = (chunks, pairs)
        return [{"head": h, "tail": t, "score": s} for h, t, s in pairs]

def make_chunks():
    metas = [
        {"summary": "A", "file_id": "fid"},
        {"summary": "B", "file_id": "fid"},
        {"summary": "C", "file_id": "fid"},
    ]
    ids = ["a", "b", "c"]
    texts = ["A", "B", "C"]
    return [
        ParagraphChunk(id=i, page_content=t, metadata=m)
        for i, t, m in zip(ids, texts, metas)
    ]


def test_build_and_save(tmp_path):
    retr = DummyRetriever()
    rerank = DummyReranker()
    rel_builder = DummyRelationBuilder()
    gb = GraphBuilder(retr, rerank, rel_builder, top_k=2, base_dir=tmp_path)

    chunks = make_chunks()
    relations = gb.build_and_save(chunks)

    assert rerank.inputs == ["A\nB", "A\nC", "B\nC"]
    assert relations == [
        {"head": "a", "tail": "c", "score": 0.9},
        {"head": "b", "tail": "c", "score": 0.2},
    ]

    file_path = tmp_path / "fid" / "relations.json"
    with file_path.open("r", encoding="utf-8") as f:
        saved = json.load(f)
    assert saved == relations
