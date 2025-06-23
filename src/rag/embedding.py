# src/rag/embedding.py

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from camel.embeddings import OpenAICompatibleEmbedding
from camel.storages import BaseVectorStorage, VectorRecord, QdrantStorage
from camel.types import VectorDistance
from src.datamodel import ParagraphChunk

load_dotenv()

class EmbeddingManager:
    def __init__(self, config: dict, collection_name: str):
        self.embedder = OpenAICompatibleEmbedding(
            model_type=config["model_name"],
            url=config["url"],
        )
        self.batch_size = config.get("batch_size", 32)
        # 初始化向量存储路径并绑定本地 QdrantStorage
        self.index_path = Path(config.get("index_path", "data/vector_store"))
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self.storage = QdrantStorage(
            vector_dim=self.embedder.get_output_dim(),
            path=str(self.index_path),
            collection_name=collection_name,
            distance=VectorDistance.COSINE,
        )

    def build_or_load(self, documents: List[ParagraphChunk], force_rebuild: bool = False):
        """
        如果已有索引且不强制重建，直接加载；否则对所有 documents 批量计算嵌入并存储。
        """
        # 使用 index_path 判断本地目录是否非空
        if any(self.index_path.iterdir()) and not force_rebuild:
            self.storage.load()
            return

        # 批量计算并存储
        for i in range(0, len(documents), self.batch_size):
            batch = documents[i : i + self.batch_size]
            texts = [d.page_content for d in batch]
            vectors = self.embedder.embed_list(texts)

            # 构造 VectorRecord
            records = []
            for vec, doc in zip(vectors, batch):
                vr = VectorRecord(
                    id=doc.id,
                    vector=vec,
                    payload={
                        "text": doc.page_content,  # 正文
                        "metadata": doc.metadata,  # 页码、文件名
                        "content path": f"{doc.metadata['file_id']}#page="
                                        f"{doc.metadata['page_num']}",
                        "extra_info": {}  # 可选
                    }
                )
                records.append(vr)

            # 重点：传入 records 参数
            self.storage.add(records=records)

    def embed(self, text: str) -> list[float]:
        """对单条文本进行编码。"""
        return self.embedder.embed_list([text])[0]