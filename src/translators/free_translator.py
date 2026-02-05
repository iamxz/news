"""
免费翻译器

使用开源翻译库，如 googletrans (Google Translate 免费接口)
"""
from typing import Optional
import time

try:
    from googletrans import Translator
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False
    print("警告: googletrans 未安装。请运行 'pip install googletrans==4.0.0rc1'")

from src.translators.base import BaseTranslator
from src.utils.logger import logger


class FreeTranslator(BaseTranslator):
    """免费翻译器（使用 googletrans 库）"""
    
    def __init__(self):
        super().__init__("Free Translator")
        
        if GOOGLETRANS_AVAILABLE:
            self.translator = Translator()
            logger.info(f"[{self.name}] 翻译器初始化成功")
        else:
            self.translator = None
            logger.warning(f"[{self.name}] 翻译器初始化失败：缺少 googletrans 库")
    
    def translate(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "zh"
    ) -> Optional[str]:
        """
        使用 googletrans 翻译文本

        Args:
            text: 要翻译的文本
            source_lang: 源语言代码
            target_lang: 目标语言代码

        Returns:
            翻译后的文本
        """
        if not GOOGLETRANS_AVAILABLE:
            logger.error(f"[{self.name}] 翻译器不可用：缺少 googletrans 库")
            return None
            
        if not text or not text.strip():
            return ""
        
        try:
            # googletrans 使用的语言代码可能略有不同，特别是中文
            # en -> en, zh -> zh, zh-cn -> zh-cn
            src_lang = source_lang.lower()
            tgt_lang = target_lang.lower()
            
            # 特殊处理中文语言代码
            if target_lang.lower() == "zh":
                tgt_lang = "zh-cn"  # googletrans 通常使用 zh-cn 而不是 zh
            
            # 使用 googletrans 翻译
            result = self.translator.translate(
                text,
                src=src_lang,
                dest=tgt_lang
            )
            
            translation = result.text
            logger.debug(f"[{self.name}] 翻译成功: {text[:50]}...")
            
            return translation
            
        except Exception as e:
            logger.error(f"[{self.name}] 翻译失败: {e}", exc_info=True)
            return None
    
    def translate_batch(
        self,
        texts: list[str],
        source_lang: str = "en",
        target_lang: str = "zh"
    ) -> list[Optional[str]]:
        """
        批量翻译

        Args:
            texts: 文本列表
            source_lang: 源语言代码
            target_lang: 目标语言代码

        Returns:
            翻译结果列表
        """
        if not GOOGLETRANS_AVAILABLE:
            logger.error(f"[{self.name}] 翻译器不可用：缺少 googletrans 库")
            return [None] * len(texts)
        
        results = []
        for i, text in enumerate(texts):
            result = self.translate(text, source_lang, target_lang)
            results.append(result)
            
            # 避免请求过于频繁
            if i < len(texts) - 1:
                time.sleep(1)
        
        return results