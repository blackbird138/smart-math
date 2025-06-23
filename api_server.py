from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from tempfile import NamedTemporaryFile
from pathlib import Path
import shutil
from src.pipeline import SmartMathPipeline

app = FastAPI()

app.mount("/files", StaticFiles(directory="data"), name="files")

pipeline = SmartMathPipeline(name="test")

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    with NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    file_id, docs = pipeline.ingest_pdf(tmp_path)
    shutil.move(tmp_path, Path("data") / f"{file_id}.pdf")
    return {"indexed": len(docs), "file_id": file_id}

@app.get("/search")
async def search(q: str, top_k: int = 5):
    results = pipeline.search(q, top_k=top_k)
    return {"results": results}
