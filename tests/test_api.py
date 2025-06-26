from starlette.testclient import TestClient
from pathlib import Path
import json

from api_server import app, file_docs
from src.datamodel import ParagraphChunk

client = TestClient(app)

FILE_ID = "testfile"
DATA_PATH = Path(__file__).parent / "data" / "chunks_filtered.json"

with DATA_PATH.open("r", encoding="utf-8") as f:
    json_list = json.load(f)
    docs = [ParagraphChunk.from_json(s) for s in json_list]
file_docs[FILE_ID] = docs


def test_list_chunks_filter():
    res = client.get(f"/list_chunks?file_id={FILE_ID}&chunk_type=definition")
    assert res.status_code == 200
    data = res.json()
    assert data["chunks"]
    assert all(c["chunk_type"] == "definition" for c in data["chunks"])


def test_get_chunk():
    cid = docs[0].id
    res = client.get(f"/get_chunk?file_id={FILE_ID}&chunk_id={cid}")
    assert res.status_code == 200
    data = res.json()
    assert data["content"] == docs[0].page_content
    assert data["chunk_type"] == docs[0].metadata.get("chunk_type", "")


def test_get_chunk_not_found():
    res = client.get(f"/get_chunk?file_id={FILE_ID}&chunk_id=missing")
    assert res.status_code == 404


def test_solve(monkeypatch):
    def fake_solve(self, q):
        return "dummy"

    monkeypatch.setattr("api_server.MathSolver.solve", fake_solve)
    res = client.post("/solve", json={"file_id": FILE_ID, "question": "test"})
    assert res.status_code == 200
    assert res.json()["answer"] == "dummy"


def test_solve_sanitizes(monkeypatch):
    captured = {}

    def fake_solve(self, q):
        captured["q"] = q
        return "dummy"

    monkeypatch.setattr("api_server.MathSolver.solve", fake_solve)
    res = client.post(
        "/solve",
        json={"file_id": FILE_ID, "question": "包含暴力指令"},
    )
    assert res.status_code == 200
    assert "暴力" not in captured["q"]

