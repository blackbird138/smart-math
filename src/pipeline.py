import yaml
from pathlib import Path
from typing import List

from src.loaders.mineru_loader import load_json_by_mineru
from src.preprocessing.cleaner import clean_documents
from src.preprocessing.filterer import chunk_and_filter
from src.rag.embedding import EmbeddingManager
from src.rag.retriever import RetrieverManager


class SmartMathPipeline:
    """Simple pipeline that wires the project modules together."""

    def __init__(self, config_path: str = "config/rag_config.yaml", index_path: str | Path | None = None):
        self.cfg = yaml.safe_load(Path(config_path).read_text())
        self.embedding_mgr = EmbeddingManager(self.cfg["embedding"])
        idx_path = Path(index_path or "vector_store")
        idx_path.mkdir(parents=True, exist_ok=True)

        from camel.storages import QdrantStorage, VectorDistance
        storage = QdrantStorage(
            vector_dim=self.embedding_mgr.embedder.get_output_dim(),
            path=str(idx_path),
            distance=VectorDistance.COSINE,
        )
        self.embedding_mgr.bind_storage(storage)
        self.retriever_mgr = RetrieverManager(self.embedding_mgr, self.cfg["retriever"])

    def ingest_pdf(self, path: str) -> tuple[str, List[dict]]:
        """Parse PDF, clean and chunk it, then index the chunks."""
        file_id, docs = load_json_by_mineru(path)
        docs = clean_documents(docs)
        docs = chunk_and_filter(docs)
        self.embedding_mgr.build_or_load(docs, force_rebuild=True)
        return file_id, docs

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        return self.retriever_mgr.retrieve(query, top_k=top_k)


__all__ = ["SmartMathPipeline"]

