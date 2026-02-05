"""
OpenAI 翻译器

使用 OpenAI API 进行翻译
"""
from typing import Optional
import time

from openai import OpenAI

from src.translators.base import BaseTranslator
from src.utils.config import get_settings
from src.utils.logger import logger


class OpenAITranslator(BaseTranslator):
    """OpenAI 翻译器"""
    
    def __init__(self):
        super().__init__("OpenAI")
        self.settings = get_settings()
        
        if not self.settings.openai_api_key:
            logger.warning("OpenAI API key 未配置")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.settings.openai_api_key)
    
    def translate(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "zh"
    ) -> Optional[str]:
        """
        使用 OpenAI 翻译文本
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言代码
            target_lang: 目标语言代码
        
        Returns:
            翻译后的文本
        """
        if not self.client:
            logger.error("OpenAI 客户端未初始化")
            return None
        
        if not text or not text.strip():
            return ""
        
        try:
            # 构建提示词
            lang_map = {
                "en": "英文",
                "zh": "中文",
                "ja": "日文",
                "ko": "韩文",
            }
            
            source_lang_name = lang_map.get(source_lang, source_lang)
            target_lang_name = lang_map.get(target_lang, target_lang)
            
            prompt = f"""请将以下{source_lang_name}新闻翻译成{target_lang_name}。
要求：
1. 保持专业术语的准确性
2. 保持新闻的客观性和中立性
3. 确保翻译流畅自然
4. 不要添加任何解释或评论
5. 直接输出翻译结果

原文：
{text}

翻译："""
            
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的新闻翻译助手，擅长准确、客观地翻译新闻内容。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # 降低温度以获得更一致的翻译
                max_tokens=2000
            )
            
            translation = response.choices[0].message.content.strip()
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
        批量翻译（逐个翻译以确保质量）
        
        Args:
            texts: 文本列表
            source_lang: 源语言代码
            target_lang: 目标语言代码
        
        Returns:
            翻译结果列表
        """
        results = []
        for i, text in enumerate(texts):
            logger.info(f"[{self.name}] 翻译进度: {i+1}/{len(texts)}")
            result = self.translate(text, source_lang, target_lang)
            results.append(result)
            
            # 添加延迟避免速率限制
            if i < len(texts) - 1:
                time.sleep(0.5)
        
        return results
