from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import set_key
import os
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from tempfile import NamedTemporaryFile
from pathlib import Path
import shutil
import json
import yaml
from src.loaders.mineru_loader import load_json_by_mineru
from src.preprocessing.cleaner import clean_documents
from src.preprocessing.filterer import chunk_and_filter
from src.rag.embedding import EmbeddingManager
from src.rag.retriever import RetrieverManager
from src.graph import GraphBuilder
from src.graph.pair_reranker import PairReranker
from src.graph.relation_builder import RelationBuilder
from src.datamodel import ParagraphChunk

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/files", StaticFiles(directory="data"), name="files")

# 加载 RAG 与 Agent 配置
with open(Path("config") / "rag_config.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
with open(Path("config") / "agent_config.yaml", "r", encoding="utf-8") as f:
    agent_cfg = yaml.safe_load(f)

# 按文件缓存对应的索引管理器及切片内容
file_managers: dict[str, RetrieverManager] = {}
file_docs: dict[str, list[ParagraphChunk]] = {}


class EnvUpdate(BaseModel):
    SILICONFLOW_API_KEY: str | None = None
    OPENAI_COMPATIBILITY_API_KEY: str | None = None


@app.post("/update_env")
async def update_env(data: EnvUpdate):
    """更新服务器环境变量并写入 .env 文件"""
    env_file = Path(".env")
    if data.SILICONFLOW_API_KEY is not None:
        os.environ["SILICONFLOW_API_KEY"] = data.SILICONFLOW_API_KEY
        set_key(str(env_file), "SILICONFLOW_API_KEY", data.SILICONFLOW_API_KEY)
    if data.OPENAI_COMPATIBILITY_API_KEY is not None:
        os.environ["OPENAI_COMPATIBILITY_API_KEY"] = data.OPENAI_COMPATIBILITY_API_KEY
        set_key(str(env_file), "OPENAI_COMPATIBILITY_API_KEY", data.OPENAI_COMPATIBILITY_API_KEY)
    return {"status": "ok"}

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
    file_docs[file_id] = docs

    # 保存切片以便后续构建关系图
    save_dir = Path("data/relation_store") / file_id
    save_dir.mkdir(parents=True, exist_ok=True)
    with (save_dir / "chunks.json").open("w", encoding="utf-8") as f:
        json.dump([c.to_json() for c in docs], f, ensure_ascii=False, indent=2)

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


@app.post("/build_graph")
async def build_graph(file_id: str, top_k: int = 5):
    """构建指定文件的关系图并保存"""
    retr = file_managers.get(file_id)
    if retr is None:
        emb_mgr = EmbeddingManager(cfg["embedding"], file_id)
        try:
            emb_mgr.storage.status()
        except Exception:
            raise HTTPException(status_code=404, detail="file_id not found")
        retr = RetrieverManager(emb_mgr, cfg["retriever"])
        file_managers[file_id] = retr

    chunks = file_docs.get(file_id)
    if chunks is None:
        chunks_path = Path("data/relation_store") / file_id / "chunks.json"
        if not chunks_path.exists():
            raise HTTPException(status_code=404, detail="chunks not found")
        with chunks_path.open("r", encoding="utf-8") as f:
            json_list = json.load(f)
            chunks = [ParagraphChunk.from_json(s) for s in json_list]
        file_docs[file_id] = chunks

    gb = GraphBuilder(
        retr,
        PairReranker(),
        RelationBuilder(agent_cfg),
        file_id=file_id,
        top_k=top_k,
        base_dir="data/relation_store",
    )
    relations = gb.build_and_save(chunks)
    return {"relations": relations}

@app.get("/list_chunks")
async def list_chunks(file_id: str):
    """列出指定文件的所有已处理 chunk"""
    chunks = file_docs.get(file_id)
    if chunks is None:
        path = Path("data/relation_store") / file_id / "chunks.json"
        if not path.exists():
            raise HTTPException(status_code=404, detail="chunks not found")
        with path.open("r", encoding="utf-8") as f:
            json_list = json.load(f)
            chunks = [ParagraphChunk.from_json(s) for s in json_list]
        file_docs[file_id] = chunks
    return {"chunks": [
        {
            "id": c.id,
            "summary": c.metadata.get("summary", ""),
            "content": c.page_content,
            "chunk_type": c.metadata.get("chunk_type", ""),
            "page_num": c.metadata.get("page_num"),
            "number": c.metadata.get("number", "")
        }
        for c in chunks
    ]}

@app.get("/list_related")
async def list_related(file_id: str, chunk_id: str):
    """列出与指定 chunk 相关的所有 chunk"""
    rel_path = Path("data/relation_store") / file_id / "relations.json"
    if not rel_path.exists():
        # 若关系文件不存在则尝试构建
        await build_graph(file_id)
    with rel_path.open("r", encoding="utf-8") as f:
        relations = json.load(f)
    related_ids = [
        (r["tail"] if r["head"] == chunk_id else r["head"], r)
        for r in relations if r["head"] == chunk_id or r["tail"] == chunk_id
    ]
    chunks = file_docs.get(file_id)
    if chunks is None:
        path = Path("data/relation_store") / file_id / "chunks.json"
        if not path.exists():
            raise HTTPException(status_code=404, detail="chunks not found")
        with path.open("r", encoding="utf-8") as f:
            json_list = json.load(f)
            chunks = [ParagraphChunk.from_json(s) for s in json_list]
        file_docs[file_id] = chunks
    id_map = {c.id: c for c in chunks}
    result = []
    for cid, rel in related_ids:
        c = id_map.get(cid)
        if c:
            result.append({
                "id": c.id,
                "summary": c.metadata.get("summary", ""),
                "relation": rel.get("relation_type", ""),
                "relation_summary": rel.get("summary", ""),
                "chunk_type": c.metadata.get("chunk_type", ""),
                "page_num": c.metadata.get("page_num"),
                "number": c.metadata.get("number", "")
            })
    return {"related": result}
