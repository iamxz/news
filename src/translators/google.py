"""
Google 翻译器

使用 requests 直接调用 Google Translate API（免费的 Web 接口）
"""
from typing import Optional
import requests
import json
import time

from src.translators.base import BaseTranslator
from src.utils.logger import logger


class GoogleTranslator(BaseTranslator):
    """Google 翻译器（使用免费 API）"""
    
    def __init__(self):
        super().__init__("Google Translate")
        
        # Google Translate API 免费接口
        self.api_url = "https://translate.googleapis.com/translate_a/single"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        logger.info(f"[{self.name}] 翻译器初始化成功")
    
    def translate(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "zh"
    ) -> Optional[str]:
        """
        使用 Google Translate 翻译文本
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言代码
            target_lang: 目标语言代码
        
        Returns:
            翻译后的文本
        """
        if not text or not text.strip():
            return ""
        
        try:
            # Google Translate 参数
            params = {
                'client': 'gtx',  # 使用 gtx 客户端，可以绕过一些限制
                'sl': source_lang,  # 源语言
                'tl': target_lang,  # 目标语言
                'dt': 't',  # 翻译文本
                'q': text  # 要翻译的文本
            }
            
            # 发送请求
            response = self.session.get(
                self.api_url,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            # 提取翻译结果
            if isinstance(result, list) and len(result) > 0:
                translated_text = ""
                for item in result[0]:
                    if isinstance(item, list) and len(item) > 0 and item[0]:
                        translated_text += item[0]
                
                logger.debug(f"[{self.name}] 翻译成功: {text[:50]}...")
                return translated_text.strip()
            else:
                logger.error(f"[{self.name}] 翻译结果格式异常")
                return None
            
        except requests.RequestException as e:
            logger.error(f"[{self.name}] 网络请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"[{self.name}] JSON 解析失败: {e}")
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
        results = []
        for i, text in enumerate(texts):
            result = self.translate(text, source_lang, target_lang)
            results.append(result)
            
            # 避免请求过快
            if i < len(texts) - 1:
                time.sleep(1)
        
        return results
