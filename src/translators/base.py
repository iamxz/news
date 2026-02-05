"""
翻译器基类

所有翻译服务的基类
"""
from abc import ABC, abstractmethod
from typing import Optional

from src.utils.logger import logger


class BaseTranslator(ABC):
    """翻译器基类"""
    
    def __init__(self, name: str):
        """
        初始化翻译器
        
        Args:
            name: 翻译器名称
        """
        self.name = name
    
    @abstractmethod
    def translate(self, text: str, source_lang: str = "en", target_lang: str = "zh") -> Optional[str]:
        """
        翻译文本（需要子类实现）
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言代码
            target_lang: 目标语言代码
        
        Returns:
            翻译后的文本，失败返回 None
        """
        pass
    
    def translate_batch(
        self,
        texts: list[str],
        source_lang: str = "en",
        target_lang: str = "zh"
    ) -> list[Optional[str]]:
        """
        批量翻译文本
        
        Args:
            texts: 文本列表
            source_lang: 源语言代码
            target_lang: 目标语言代码
        
        Returns:
            翻译结果列表
        """
        results = []
        for text in texts:
            result = self.translate(text, source_lang, target_lang)
            results.append(result)
        return results
    
    def is_available(self) -> bool:
        """
        检查翻译服务是否可用
        
        Returns:
            是否可用
        """
        try:
            # 尝试翻译一个简单的测试文本
            result = self.translate("Hello", "en", "zh")
            return result is not None
        except Exception:
            return False
