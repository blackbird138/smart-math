import os

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod

app = FastAPI()
@app.get("/health")
def health():
    return {"status": "ok"}

# prepare env
local_image_dir, local_md_dir = "/data/mineru/images", "/data/mineru"
image_dir = str(os.path.basename(local_image_dir))

os.makedirs(local_image_dir, exist_ok=True)

image_writer, md_writer = FileBasedDataWriter(local_image_dir), FileBasedDataWriter(
    local_md_dir
)

@app.post("/parse")
async def parse(
    file: UploadFile = File(...),
    dump_md: bool = Form(False),
    draw_layout: bool = Form(False)
):
    name_without_suff = file.filename.split(".")[0]

    pdf_bytes = await file.read()              # 读取上传文件
    ds = PymuDocDataset(pdf_bytes)

    # 判定 TXT / OCR，决定是否打开 OCR
    if ds.classify() == SupportedPdfParseMethod.OCR:
        infer_result = ds.apply(doc_analyze, ocr=True)
        pipe_result = infer_result.pipe_ocr_mode(image_writer)

    else:
        infer_result = ds.apply(doc_analyze, ocr=False)
        pipe_result = infer_result.pipe_txt_mode(image_writer)

    if dump_md == True:
        pipe_result.dump_md(md_writer, f"{name_without_suff}.md", image_dir)

    if draw_layout == True:
        pipe_result.draw_layout(os.path.join(local_md_dir, f"{name_without_suff}_layout.pdf"))

    # 导出中间格式（含 para_blocks、bbox 等）
    content_list_content = pipe_result.get_content_list(image_dir)
    pipe_result.dump_content_list(md_writer, f"{name_without_suff}_content_list.json", image_dir)

    return JSONResponse(content=content_list_content)
