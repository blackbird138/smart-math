# src/utils/logger.py

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    创建并返回一个 Logger 实例：
      - 控制台输出
      - 日志文件（滚动写入，单文件最大10MB，保留3个备份）
      - 统一的日志格式：时间 级别 [模块:行号] 消息
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 日志输出格式
    fmt = logging.Formatter(
        "%(asctime)s %(levelname)-8s [%(module)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台 Handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # 文件 Handler（滚动日志）
    fh = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=3,
        encoding="utf-8",
    )
    fh.setLevel(level)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger
