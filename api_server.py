from fastapi import FastAPI, UploadFile, File
from tempfile import NamedTemporaryFile
from pathlib import Path
from src.pipeline import SmartMathPipeline

app = FastAPI()

pipeline = SmartMathPipeline()

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    with NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    docs = pipeline.ingest_pdf(tmp_path)
    Path(tmp_path).unlink(missing_ok=True)
    return {"indexed": len(docs)}

@app.get("/search")
async def search(q: str, top_k: int = 5):
    results = pipeline.search(q, top_k=top_k)
    return {"results": results}
