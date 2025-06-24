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
