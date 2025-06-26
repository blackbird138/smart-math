# src/graph/siliconflow_reranker.py
"""Siliconflow 重排序接口封装。

依照官方示例，通过 HTTP 请求 ``/v1/rerank`` 接口获得得分。API
Key 需放在 ``SILICONFLOW_API_KEY`` 环境变量中。"""

from typing import List
import os
import requests


class SiliconflowReranker:
    """调用 Siliconflow 服务获取重排序得分."""

    def __init__(self, model: str = "BAAI/bge-reranker-v2-m3",
                 url: str = "https://api.siliconflow.cn/v1/rerank") -> None:
        self.model = model
        self.url = url
        token = os.getenv("SILICONFLOW_API_KEY")
        if not token:
            raise RuntimeError("SILICONFLOW_API_KEY not set")
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def rerank(self, query: str, documents: List[str]) -> List[float]:
        payload = {"model": self.model, "query": query, "documents": documents}
        res = requests.post(self.url, json=payload, headers=self.headers, timeout=10)
        res.raise_for_status()
        data = res.json()
        # 兼容可能的多种返回格式
        if isinstance(data, dict):
            if "results" in data:
                results = data["results"]
                if results and isinstance(results[0], dict) and "score" in results[0]:
                    return [r["score"] for r in results]
                return results
            if "scores" in data:
                return data["scores"]
        if isinstance(data, list):
            if data and isinstance(data[0], dict) and "score" in data[0]:
                return [d["score"] for d in data]
            return data
        raise ValueError("Unexpected response format")
