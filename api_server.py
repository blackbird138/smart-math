from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from tempfile import NamedTemporaryFile
from pathlib import Path
import shutil
import yaml
from src.loaders.mineru_loader import load_json_by_mineru
from src.preprocessing.cleaner import clean_documents
from src.preprocessing.filterer import chunk_and_filter
from src.rag.embedding import EmbeddingManager
from src.rag.retriever import RetrieverManager

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/files", StaticFiles(directory="data"), name="files")

# 加载 RAG 配置
with open(Path("config") / "rag_config.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

# 按文件缓存对应的索引管理器
file_managers: dict[str, RetrieverManager] = {}

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    """上传并索引单个 PDF 文件"""
    with NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # 解析并切分文档
    file_id, docs = load_json_by_mineru(tmp_path)
    docs = clean_documents(docs)
    docs = chunk_and_filter(docs)

    # 构建针对该文件的向量索引
    emb_mgr = EmbeddingManager(cfg["embedding"], file_id)
    emb_mgr.build_or_load(docs, force_rebuild=True)
    retr_mgr = RetrieverManager(emb_mgr, cfg["retriever"])
    file_managers[file_id] = retr_mgr

    shutil.move(tmp_path, Path("data") / f"{file_id}.pdf")
    return {"indexed": len(docs), "file_id": file_id}

@app.get("/search")
async def search(q: str, file_id: str, top_k: int = 5):
    """根据 file_id 在对应索引中检索"""
    retr = file_managers.get(file_id)
    if retr is None:
        # 若未找到，则尝试加载已有索引
        emb_mgr = EmbeddingManager(cfg["embedding"], file_id)
        try:
            # 若索引不存在会抛错，由用户自行确认
            emb_mgr.storage.status()
        except Exception:
            raise HTTPException(status_code=404, detail="file_id not found")
        retr = RetrieverManager(emb_mgr, cfg["retriever"])
        file_managers[file_id] = retr

    results = retr.retrieve(q, top_k=top_k)
    return {"results": results}


@app.get("/list_files")
async def list_files():
    """返回 data 目录下已上传的文件列表"""
    ids = [p.stem for p in Path("data").glob("*.pdf")]
    return {"files": ids}
