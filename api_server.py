from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import asyncio
from pydantic import BaseModel
from dotenv import set_key
import os
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from tempfile import NamedTemporaryFile
from pathlib import Path
from PIL import Image
import requests
from io import BytesIO
import shutil
import json
import yaml
from src.utils.logger import get_logger
from src.loaders.mineru_loader import load_json_by_mineru
from src.preprocessing.cleaner import clean_documents
from src.preprocessing.filterer import chunk_and_filter
from src.rag.embedding import EmbeddingManager
from src.rag.retriever import RetrieverManager
from src.graph import GraphBuilder
from src.graph.pair_reranker import PairReranker
from src.graph.relation_builder import RelationBuilder
from src.datamodel import ParagraphChunk
from src.solver import MathSolver, ConversationMemory
from src.utils.preprocess import sanitize_prompt

logger = get_logger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/files", StaticFiles(directory="data"), name="files")

# 加载 RAG 与 Agent 配置
BASE_DIR = Path(__file__).resolve().parent
with open(BASE_DIR / "config" / "rag_config.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
with open(BASE_DIR / "config" / "agent_config.yaml", "r", encoding="utf-8") as f:
    agent_cfg = yaml.safe_load(f)

# 按文件缓存对应的索引管理器及切片内容
file_managers: dict[str, RetrieverManager] = {}
file_docs: dict[str, list[ParagraphChunk]] = {}
file_memories: dict[str, ConversationMemory] = {}

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
    logger.info("Environment variables updated")
    return {"status": "ok"}

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    """上传并索引单个 PDF 文件"""
    logger.info("Received file upload: %s", file.filename)
    with NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # 解析并切分文档
    file_id, docs = load_json_by_mineru(tmp_path)
    docs = clean_documents(docs)
    docs = chunk_and_filter(docs)
    file_docs[file_id] = docs
    file_memories[file_id] = ConversationMemory()

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
    logger.info("Indexed %d chunks for %s", len(docs), file_id)

    shutil.move(tmp_path, Path("data") / f"{file_id}.pdf")
    return {"indexed": len(docs), "file_id": file_id}


@app.get("/search")
async def search(q: str, file_id: str, top_k: int = 5):
    """根据 file_id 在对应索引中检索"""
    logger.info("Search query: %s for file %s", q, file_id)
    retr = file_managers.get(file_id)
    if retr is None:
        # 若未找到，则尝试加载已有索引
        emb_mgr = EmbeddingManager(cfg["embedding"], file_id)
        try:
            # 若索引不存在会抛错，由用户自行确认
            emb_mgr.storage.status()
        except Exception as e:
            logger.error("Load index failed: %s", e)
            raise HTTPException(status_code=404, detail="file_id not found")
        retr = RetrieverManager(emb_mgr, cfg["retriever"])
        file_managers[file_id] = retr

    results = retr.retrieve(q, top_k=top_k)
    logger.info("Found %d results", len(results))
    return {"results": results}


@app.get("/list_files")
async def list_files():
    """返回 data 目录下已上传的文件列表"""
    ids = [p.stem for p in Path("data").glob("*.pdf")]
    return {"files": ids}


@app.post("/image_ocr")
async def image_ocr(file: UploadFile = File(...)):
    """识别上传图片中的数学公式并返回 LaTeX"""
    logger.info("OCR image uploaded: %s", file.filename)
    with NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        image = Image.open(tmp_path).convert("RGB")
        pdf_buffer = BytesIO()
        image.save(pdf_buffer, format="PDF")
        pdf_buffer.seek(0)

        res = requests.post(
            "http://localhost:8000/parse",
            files={"file": ("image.pdf", pdf_buffer.getvalue(), "application/pdf")},
            data={"dump_md": False, "draw_layout": False},
            timeout=60,
        )
        res.raise_for_status()
        blocks = res.json()
        equations = [b["text"] for b in blocks if "text" in b]
        latex = "\n".join(equations) if equations else ""
        return {"latex": latex}
    finally:
        os.remove(tmp_path)


@app.post("/build_graph")
async def build_graph(file_id: str, top_k: int = 5):
    """构建指定文件的关系图并保存"""
    logger.info("Building graph for %s", file_id)
    retr = file_managers.get(file_id)
    if retr is None:
        emb_mgr = EmbeddingManager(cfg["embedding"], file_id)
        try:
            emb_mgr.storage.status()
        except Exception as e:
            logger.error("Load index failed: %s", e)
            raise HTTPException(status_code=404, detail="file_id not found")
        retr = RetrieverManager(emb_mgr, cfg["retriever"])
        file_managers[file_id] = retr

    chunks = file_docs.get(file_id)
    if chunks is None:
        chunks_path = Path("data/relation_store") / file_id / "chunks.json"
        if not chunks_path.exists():
            logger.error("Chunks not found for %s", file_id)
            raise HTTPException(status_code=404, detail="chunks not found")
        with chunks_path.open("r", encoding="utf-8") as f:
            json_list = json.load(f)
            chunks = [ParagraphChunk.from_json(s) for s in json_list]
        file_docs[file_id] = chunks

    gb = GraphBuilder(
        retr,
        PairReranker(),
        RelationBuilder(agent_cfg["PROCESS_MODEL"]),
        file_id=file_id,
        top_k=top_k,
        base_dir="data/relation_store",
    )
    relations = gb.build_and_save(chunks)
    logger.info("Graph built with %d relations", len(relations))
    return {"relations": relations}


@app.get("/list_chunks")
async def list_chunks(file_id: str, chunk_type: str | None = None):
    """列出指定文件的所有已处理 chunk

    :param file_id: 目标文件 ID
    :param chunk_type: 以逗号分隔的 chunk 类型，可选
    """
    chunks = file_docs.get(file_id)
    if chunks is None:
        path = Path("data/relation_store") / file_id / "chunks.json"
        if not path.exists():
            logger.error("Chunks not found for %s", file_id)
            raise HTTPException(status_code=404, detail="chunks not found")
        with path.open("r", encoding="utf-8") as f:
            json_list = json.load(f)
            chunks = [ParagraphChunk.from_json(s) for s in json_list]
        file_docs[file_id] = chunks

    if chunk_type:
        allow = {t.strip().lower() for t in chunk_type.split(",") if t}
        chunks = [
            c for c in chunks if c.metadata.get("chunk_type", "").lower() in allow
        ]

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
        for r in relations
        if r["head"] == chunk_id or r["tail"] == chunk_id
    ]
    chunks = file_docs.get(file_id)
    if chunks is None:
        path = Path("data/relation_store") / file_id / "chunks.json"
        if not path.exists():
            logger.error("Chunks not found for %s", file_id)
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


@app.get("/get_chunk")
async def get_chunk(file_id: str, chunk_id: str):
    """根据 ID 获取指定 chunk 的内容、类型及编号"""
    chunks = file_docs.get(file_id)
    if chunks is None:
        path = Path("data/relation_store") / file_id / "chunks.json"
        if not path.exists():
            logger.error("Chunks not found for %s", file_id)
            raise HTTPException(status_code=404, detail="chunks not found")
        with path.open("r", encoding="utf-8") as f:
            json_list = json.load(f)
            chunks = [ParagraphChunk.from_json(s) for s in json_list]
        file_docs[file_id] = chunks

    for c in chunks:
        if c.id == chunk_id:
            return {
                "content": c.page_content,
                "chunk_type": c.metadata.get("chunk_type", ""),
                "number": c.metadata.get("number", ""),
            }

    logger.error("Chunk %s not found in %s", chunk_id, file_id)
    raise HTTPException(status_code=404, detail="chunk not found")


class SolveRequest(BaseModel):
    file_id: str
    question: str
    top_k: int | None = 3


@app.post("/solve")
async def solve(req: SolveRequest):
    """调用 LLM 解答数学问题"""
    logger.info("Solve request for %s", req.file_id)
    retr = file_managers.get(req.file_id)
    docs = file_docs.get(req.file_id)
    if docs is None:
        path = Path("data/relation_store") / req.file_id / "chunks.json"
        if not path.exists():
            logger.error("Chunks not found for %s", req.file_id)
            raise HTTPException(status_code=404, detail="chunks not found")
        with path.open("r", encoding="utf-8") as f:
            json_list = json.load(f)
            docs = [ParagraphChunk.from_json(s) for s in json_list]
        file_docs[req.file_id] = docs
    if retr is None:
        try:
            emb_mgr = EmbeddingManager(cfg["embedding"], req.file_id)
            emb_mgr.storage.status()
            retr = RetrieverManager(emb_mgr, cfg["retriever"])
        except Exception as e:
            logger.error("Load index failed: %s", e)
            retr = None
        file_managers[req.file_id] = retr
    memory = file_memories.get(req.file_id)
    if memory is None:
        memory = ConversationMemory()
        file_memories[req.file_id] = memory
    solver = MathSolver(retr, docs, memory)
    question = sanitize_prompt(req.question)
    answer = solver.solve(question)
    logger.info("Answer generated")
    return {"answer": answer}


@app.post("/solve_stream")
async def solve_stream(req: SolveRequest):
    """流式返回数学问题的解答"""
    logger.info("Solve stream request for %s", req.file_id)
    retr = file_managers.get(req.file_id)
    docs = file_docs.get(req.file_id)
    if docs is None:
        path = Path("data/relation_store") / req.file_id / "chunks.json"
        if not path.exists():
            logger.error("Chunks not found for %s", req.file_id)
            raise HTTPException(status_code=404, detail="chunks not found")
        with path.open("r", encoding="utf-8") as f:
            json_list = json.load(f)
            docs = [ParagraphChunk.from_json(s) for s in json_list]
        file_docs[req.file_id] = docs
    if retr is None:
        try:
            emb_mgr = EmbeddingManager(cfg["embedding"], req.file_id)
            emb_mgr.storage.status()
            retr = RetrieverManager(emb_mgr, cfg["retriever"])
        except Exception as e:
            logger.error("Load index failed: %s", e)
            retr = None
        file_managers[req.file_id] = retr
    memory = file_memories.get(req.file_id)
    if memory is None:
        memory = ConversationMemory()
        file_memories[req.file_id] = memory
    solver = MathSolver(retr, docs, memory)
    question = sanitize_prompt(req.question)
    async def gen():
        for chunk in solver.stream_solve(question):
            yield chunk.encode("utf-8")
            await asyncio.sleep(0)

    headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    return StreamingResponse(gen(), media_type="text/plain; charset=utf-8", headers=headers)

    return StreamingResponse(gen(), media_type="text/plain")
