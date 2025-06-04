# src/preprocessing/cleaner.py

from typing import List, Dict, Any
from camel.loaders import UnstructuredIO
from src.datamodel import ParagraphChunk
from dataclasses import replace

uio = UnstructuredIO()

def remove_newlines(text: str) -> str:
    return text.replace('\n', ' ')

def clean_one_piece(doc: ParagraphChunk) -> ParagraphChunk:
    options = [
        ("replace_unicode_quotes", {}),  # 替换Unicode引号
        ("clean_dashes", {}),  # 清理破折号
        ("clean_extra_whitespace", {}),  # 清理多余空白
    ]

    result = replace(doc)

    clean_page_content = uio.clean_text_data(text=result.page_content, clean_options=options)
    clean_page_content = remove_newlines(clean_page_content)

    result.page_content = clean_page_content

    return result

def clean_documents(docs: List[ParagraphChunk]) -> List[ParagraphChunk]:
    result = []

    for d in docs:
        clean_doc = clean_one_piece(d)
        result.append(clean_doc)

    return result