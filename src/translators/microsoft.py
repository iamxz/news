"""
微软翻译器

使用 Azure Translator API（免费额度）
"""
from typing import Optional
import requests
import uuid
import time

from src.translators.base import BaseTranslator
from src.utils.config import get_settings
from src.utils.logger import logger


class MicrosoftTranslator(BaseTranslator):
    """微软翻译器"""
    
    API_URL = "https://api.cognitive.microsofttranslator.com/translate"
    API_VERSION = "3.0"
    
    def __init__(self):
        super().__init__("微软翻译")
        self.settings = get_settings()
        
        # 从环境变量获取密钥和区域
        self.subscription_key = getattr(self.settings, 'microsoft_translator_key', None)
        self.region = getattr(self.settings, 'microsoft_translator_region', 'global')
        
        if not self.subscription_key:
            logger.warning(f"[{self.name}] 微软翻译密钥未配置")
            self.translator = None
        else:
            self.translator = True  # 标记已初始化
            logger.info(f"[{self.name}] 翻译器初始化成功")
    
    def translate(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "zh"
    ) -> Optional[str]:
        """
        使用微软翻译 API 翻译文本
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言代码
            target_lang: 目标语言代码
        
        Returns:
            翻译后的文本
        """
        if not self.translator:
            logger.error(f"[{self.name}] 翻译器未初始化")
            return None
        
        if not text or not text.strip():
            return ""
        
        try:
            # 微软翻译语言代码
            lang_map = {
                "zh": "zh-Hans",  # 简体中文
                "zh-tw": "zh-Hant",  # 繁体中文
            }
            
            from_lang = lang_map.get(source_lang, source_lang)
            to_lang = lang_map.get(target_lang, target_lang)
            
            # 构建请求
            endpoint = f"{self.API_URL}?api-version={self.API_VERSION}"
            params = {
                'from': from_lang,
                'to': to_lang
            }
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.subscription_key,
                'Ocp-Apim-Subscription-Region': self.region,
                'Content-type': 'application/json',
                'X-ClientTraceId': str(uuid.uuid4())
            }
            
            body = [{
                'text': text
            }]
            
            # 发送请求
            response = requests.post(
                endpoint,
                params=params,
                headers=headers,
                json=body,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 提取翻译结果
            if result and len(result) > 0 and 'translations' in result[0]:
                translation = result[0]['translations'][0]['text']
                logger.debug(f"[{self.name}] 翻译成功: {text[:50]}...")
                return translation
            else:
                logger.error(f"[{self.name}] 翻译结果为空")
                return None
            
        except requests.RequestException as e:
            logger.error(f"[{self.name}] 网络请求失败: {e}")
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
        批量翻译（微软翻译支持一次性翻译多个文本）
        
        Args:
            texts: 文本列表
            source_lang: 源语言代码
            target_lang: 目标语言代码
        
        Returns:
            翻译结果列表
        """
        if not self.translator:
            return [None] * len(texts)
        
        try:
            # 微软翻译支持批量（最多 100 个文本）
            lang_map = {
                "zh": "zh-Hans",
                "zh-tw": "zh-Hant",
            }
            
            from_lang = lang_map.get(source_lang, source_lang)
            to_lang = lang_map.get(target_lang, target_lang)
            
            endpoint = f"{self.API_URL}?api-version={self.API_VERSION}"
            params = {
                'from': from_lang,
                'to': to_lang
            }
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.subscription_key,
                'Ocp-Apim-Subscription-Region': self.region,
                'Content-type': 'application/json',
                'X-ClientTraceId': str(uuid.uuid4())
            }
            
            body = [{'text': text} for text in texts[:100]]  # 限制 100 个
            
            response = requests.post(
                endpoint,
                params=params,
                headers=headers,
                json=body,
                timeout=30
            )
            response.raise_for_status()
            
            results = response.json()
            translations = [
                result['translations'][0]['text'] if 'translations' in result else None
                for result in results
            ]
            
            return translations
            
        except Exception as e:
            logger.error(f"[{self.name}] 批量翻译失败: {e}", exc_info=True)
            # 回退到逐个翻译
            return super().translate_batch(texts, source_lang, target_lang)
