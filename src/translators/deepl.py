"""
DeepL 翻译器

使用 DeepL API 进行翻译
"""
from typing import Optional

import deepl

from src.translators.base import BaseTranslator
from src.utils.config import get_settings
from src.utils.logger import logger


class DeepLTranslator(BaseTranslator):
    """DeepL 翻译器"""
    
    def __init__(self):
        super().__init__("DeepL")
        self.settings = get_settings()
        
        if not self.settings.deepl_api_key:
            logger.warning("DeepL API key 未配置")
            self.translator = None
        else:
            self.translator = deepl.Translator(self.settings.deepl_api_key)
    
    def translate(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "zh"
    ) -> Optional[str]:
        """
        使用 DeepL 翻译文本
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言代码
            target_lang: 目标语言代码
        
        Returns:
            翻译后的文本
        """
        if not self.translator:
            logger.error("DeepL 翻译器未初始化")
            return None
        
        if not text or not text.strip():
            return ""
        
        try:
            # DeepL 语言代码映射
            lang_map = {
                "en": "EN",
                "zh": "ZH",
                "ja": "JA",
                "ko": "KO",
                "de": "DE",
                "fr": "FR",
                "es": "ES",
            }
            
            source = lang_map.get(source_lang, source_lang.upper())
            target = lang_map.get(target_lang, target_lang.upper())
            
            result = self.translator.translate_text(
                text,
                source_lang=source,
                target_lang=target
            )
            
            translation = result.text
            logger.debug(f"[{self.name}] 翻译成功: {text[:50]}...")
            
            return translation
            
        except deepl.DeepLException as e:
            logger.error(f"[{self.name}] DeepL API 错误: {e}")
            return None
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
        if not self.translator:
            logger.error("DeepL 翻译器未初始化")
            return [None] * len(texts)
        
        try:
            # DeepL 支持批量翻译
            lang_map = {
                "en": "EN",
                "zh": "ZH",
                "ja": "JA",
                "ko": "KO",
            }
            
            source = lang_map.get(source_lang, source_lang.upper())
            target = lang_map.get(target_lang, target_lang.upper())
            
            results = self.translator.translate_text(
                texts,
                source_lang=source,
                target_lang=target
            )
            
            return [r.text for r in results]
            
        except Exception as e:
            logger.error(f"[{self.name}] 批量翻译失败: {e}", exc_info=True)
            # 回退到逐个翻译
            return super().translate_batch(texts, source_lang, target_lang)
