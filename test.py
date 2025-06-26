# tests/test_preprocessing.py

import json
import pytest

from pathlib import Path
from src.preprocessing.cleaner import clean_documents
from src.preprocessing.filterer import chunk_and_filter
from src.datamodel import ParagraphChunk

DATA_DIR = Path(__file__).parent / "data" / "relation_store" / "1f7b64f2b9d94a8eae5fa0ca05fbb2ff" / "chunks.json"

with DATA_DIR.open("r", encoding="utf-8") as f:
    json_str_list = json.load(f)
    docs = [ParagraphChunk.from_json(s) for s in json_str_list]
print(docs)