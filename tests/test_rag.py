# tests/test_loader.py

import json
import yaml
import pytest

from pathlib import Path
from src.rag.embedding import EmbeddingManager
from src.rag.retriever import RetrieverManager
from src.datamodel import ParagraphChunk

DATA_DIR = Path(__file__).parent / "data" / "chunks_filtered.json"
SAVE_DIR = Path(__file__).parent / "data" / "chunks_filtered.json"

with open("../config/rag_config.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

def test_chunk_and_clean_and_filter():
    with DATA_DIR.open("r", encoding="utf-8") as f:
        json_str_list = json.load(f)
        docs = [ParagraphChunk.from_json(s) for s in json_str_list]
    emb_mgr = EmbeddingManager(cfg["embedding"], "test")
    emb_mgr.build_or_load(docs, force_rebuild=True)

    # 获取底层 QdrantStorage 实例
    storage = emb_mgr.storage

    # 调用 status() 获取 VectorDBStatus
    status = storage.status()
    # VectorDBStatus 包含 vector_count 字段，表示当前存储的向量总数
    print("Stored vectors:", status.vector_count)

    # 3. 执行检索
    retr_mgr = RetrieverManager(emb_mgr, cfg["retriever"])
    hits = retr_mgr.retrieve("代数基本定理", top_k=5)
    for item in hits:
        print(item)