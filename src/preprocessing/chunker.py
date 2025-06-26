# src/preprocessing/chunker.py

import re
import uuid
from typing import List, Dict, Any
from src.datamodel import ParagraphChunk

# 1. 定义标题正则
DOT = r"[\.．·]"  # 普通点、全角点及中点
PATTERNS = {
    "definition":   re.compile(rf"^[\s\u200b\ufeff]*(定义)\s*\d+(?:{DOT}\d+)*", re.I),
    "theorem":      re.compile(rf"^[\s\u200b\ufeff]*(定理)\s*\d+(?:{DOT}\d+)*", re.I),
    "lemma":        re.compile(rf"^[\s\u200b\ufeff]*(引理)\s*\d+(?:{DOT}\d+)*", re.I),
    "proposition":  re.compile(rf"^[\s\u200b\ufeff]*(命题)\s*\d+(?:{DOT}\d+)*", re.I),
    "example":      re.compile(rf"^[\s\u200b\ufeff]*(例题?)\s*\d+(?:{DOT}\d+)*", re.I),
    "exercise":     re.compile(rf"^[\s\u200b\ufeff]*(练习)\s*\d+(?:{DOT}\d+)*", re.I),
}

def detect_header_type(text: str) -> str | None:
    stripped = text.lstrip("\u200b\ufeff \t\r\n")
    for ctype, pat in PATTERNS.items():
        if pat.match(stripped):        # 只看段首
            return ctype
    return None

def chunk_documents(docs: List[ParagraphChunk], MAX_TOKEN: int=500) -> List[ParagraphChunk]:
    """docs 为 MinerU / 自己 loader 产生的“段落级”列表"""
    result: list[ParagraphChunk] = []
    i = 0
    while i < len(docs):
        cur = docs[i]
        ctype = detect_header_type(cur.page_content)

        if not ctype:
            i += 1
            continue

        buf_text = [cur.page_content]
        buf_meta = cur.metadata
        buf_meta["chunk_type"] = ctype
        buf_meta["initial_id"] = cur.id
        buf_meta["chunk_id"] = uuid.uuid4().hex
        tok_cnt = len(cur.page_content)

        j = i + 1
        while j < len(docs):
            nxt = docs[j]
            # 遇到下一条标题段，停止拼接
            if detect_header_type(nxt.page_content):
                break
            # 若合并后 token 超过阈值，也停止
            if tok_cnt > MAX_TOKEN:
                break
            # 否则拼接
            buf_text.append(nxt.page_content)
            tok_cnt += len(nxt.page_content)
            j += 1

        result.append(ParagraphChunk(
            id=buf_meta["chunk_id"],
            page_content=buf_text,
            metadata=buf_meta,
        ))
        i = j  # 跳过已经合并的段
    return result

# def split_by_heading(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
#     """
#     将单个 loader 输出的 dict 按标题拆分为多个小 dict。
#     """
#     text = doc["page_content"]
#     meta = doc.get("metadata", {}).copy()
#     chunks: List[Dict[str, Any]] = []
#
#     # 合并所有 PATTERNS 为一个大正则，带命名组标记类型
#     parts = []
#     for t, pat in PATTERNS.items():
#         for m in pat.finditer(text):
#             parts.append((m.start(), m.end(), t, m.group().strip()))
#     # 按出现顺序排序
#     parts.sort(key=lambda x: x[0])
#
#     # 如果没匹配到任何标题，直接返回空
#     if not parts:
#         return []
#
#     # 依次根据 match 起止位置切片
#     for idx, (start, end, ctype, heading_text) in enumerate(parts):
#         # 下一个标题的 start 用于确定当前 body 截点
#         next_start = parts[idx + 1][0] if idx + 1 < len(parts) else len(text)
#         body_text = text[end:next_start].strip()
#         full_text = heading_text + ("\n" + body_text if body_text else "")
#
#         new_meta = meta.copy()
#         new_meta["chunk_type"] = ctype
#
#         chunks.append({
#             "id": uuid.uuid4().hex,
#             "page_content": full_text,
#             "metadata": new_meta,
#         })
#
#     return chunks
#
# def chunk_documents(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     """
#     对一组 loader.docs 应用正则切分，未匹配到任何标题时保留原 doc。
#     """
#     count = 0
#     result = []
#     for d in docs:
#         sub = split_by_heading(d)
#         result.extend(sub)
#     return result