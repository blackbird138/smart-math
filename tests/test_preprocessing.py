# tests/test_preprocessing.py

import json
import pytest
from pathlib import Path
from src.preprocessing.cleaner import clean_documents
from src.preprocessing.filterer import chunk_and_filter
from src.datamodel import ParagraphChunk

DATA_DIR = Path(__file__).parent / "data" / "chunks.json"
SAVE_DIR = Path(__file__).parent / "data" / "chunks_filtered.json"

def test_chunk_and_clean_and_filter():
    with DATA_DIR.open("r", encoding="utf-8") as f:
        json_str_list = json.load(f)
        docs = [ParagraphChunk.from_json(s) for s in json_str_list]
    docs = clean_documents(docs)
    docs = chunk_and_filter(docs)
    print(docs)
    json_str = [chunk.to_json() for chunk in docs]
    with SAVE_DIR.open("w", encoding="utf-8") as f:
        json.dump(json_str, f, indent=2, ensure_ascii=False, sort_keys=True)