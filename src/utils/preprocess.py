"""Utility functions for sanitizing user prompts."""

import re

# 自定义敏感词列表，可根据需要增删
SENSITIVE_WORDS = [
    "作弊",
    "暴力",
]

# 常见危险指令的正则模式
DANGEROUS_PATTERNS = [
    r"rm\s+-rf",
    r"sudo\s+rm",
    r"del\s+/f",
    r"format\s+c:",
    r"shutdown",
    r"reboot",
]

def sanitize_prompt(text: str) -> str:
    """清理用户输入中的危险内容并返回安全文本."""
    clean = text
    # 去除危险指令
    for pat in DANGEROUS_PATTERNS:
        clean = re.sub(pat, "", clean, flags=re.IGNORECASE)

    # 替换敏感词为同长度星号
    for word in SENSITIVE_WORDS:
        clean = re.sub(word, "*" * len(word), clean, flags=re.IGNORECASE)

    return clean.strip()
