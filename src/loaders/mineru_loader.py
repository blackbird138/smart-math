# src/loaders/mineru_loader.py

import uuid
import requests
from pathlib import Path
from src.datamodel import ParagraphChunk

def MineruLoader(
    path: str,
    dump_md: bool = False,
    draw_layout: bool = False,
    url="http://localhost:8000/parse"
):
    file_path = Path(path).resolve()
    with file_path.open("rb") as f:
        res = requests.post(
            url=url,
            files={"file": f},
            data={
                "dump_md": dump_md,
                "draw_layout": draw_layout
            }
        )
    res.raise_for_status()
    return res.json()

def load_json_by_mineru(path: str):
    json_list = MineruLoader(path)
    result = []

    file_id = uuid.uuid4().hex

    for chunk in json_list:
        if chunk["type"] == "text" or chunk["type"] == "equation" or chunk["type"] == "table":
            content = ""
            if chunk["type"] == "table":
                content = chunk["table_body"]
            else:
                content = chunk["text"]
            result.append(ParagraphChunk(
                id=uuid.uuid4().hex,
                page_content=content,
                metadata={
                    "page_num": chunk["page_idx"],
                    "file_id": file_id
                }
            ))

    return (file_id, result)