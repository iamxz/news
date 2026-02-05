"""
辅助函数模块

提供通用的辅助函数
"""
import hashlib
import re
from datetime import datetime
from typing import Any, Dict, Optional
from urllib.parse import urlparse


def generate_id(text: str) -> str:
    """
    根据文本生成唯一 ID
    
    Args:
        text: 输入文本
    
    Returns:
        MD5 哈希字符串
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def clean_html(html: str) -> str:
    """
    清理 HTML 标签，返回纯文本
    
    Args:
        html: HTML 字符串
    
    Returns:
        清理后的纯文本
    """
    # 移除 HTML 标签
    clean = re.sub(r'<[^>]+>', '', html)
    # 移除多余空白
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    截断文本到指定长度
    
    Args:
        text: 输入文本
        max_length: 最大长度
        suffix: 截断后缀
    
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def is_valid_url(url: str) -> bool:
    """
    验证 URL 是否有效
    
    Args:
        url: URL 字符串
    
    Returns:
        是否有效
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def get_domain(url: str) -> str:
    """
    从 URL 中提取域名
    
    Args:
        url: URL 字符串
    
    Returns:
        域名
    """
    try:
        return urlparse(url).netloc
    except Exception:
        return ""


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期时间
    
    Args:
        dt: datetime 对象
        format_str: 格式字符串
    
    Returns:
        格式化后的字符串
    """
    return dt.strftime(format_str)


def safe_get(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    安全地从嵌套字典中获取值
    
    Args:
        data: 字典数据
        keys: 键路径
        default: 默认值
    
    Returns:
        获取到的值或默认值
    
    Example:
        >>> data = {'a': {'b': {'c': 1}}}
        >>> safe_get(data, 'a', 'b', 'c')
        1
        >>> safe_get(data, 'a', 'x', 'y', default=0)
        0
    """
    try:
        result = data
        for key in keys:
            result = result[key]
        return result
    except (KeyError, TypeError):
        return default


def remove_duplicates(items: list, key: Optional[str] = None) -> list:
    """
    去除列表中的重复项
    
    Args:
        items: 列表
        key: 如果列表元素是字典，指定用于去重的键
    
    Returns:
        去重后的列表
    """
    if not items:
        return []
    
    if key is None:
        return list(dict.fromkeys(items))
    
    seen = set()
    result = []
    for item in items:
        value = item.get(key) if isinstance(item, dict) else item
        if value not in seen:
            seen.add(value)
            result.append(item)
    return result
