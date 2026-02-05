"""
日志工具模块

提供统一的日志记录功能
"""
import logging
import sys
from pathlib import Path
from typing import Optional

from rich.logging import RichHandler


def setup_logger(
    name: str = "news",
    level: str = "INFO",
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    设置并返回配置好的日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径，如果为 None 则只输出到控制台
    
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 避免重复添加 handler
    if logger.handlers:
        return logger
    
    # Rich 控制台处理器（带颜色和格式）
    console_handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_time=True,
        show_path=False
    )
    console_handler.setFormatter(
        logging.Formatter("%(message)s", datefmt="[%X]")
    )
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定）
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )
        logger.addHandler(file_handler)
    
    return logger


# 默认日志记录器
logger = setup_logger()
