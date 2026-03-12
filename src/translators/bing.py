"""
Bing 翻译器

使用 Bing Translate 非官方接口进行翻译
"""
from typing import Optional
import requests

from src.translators.base import BaseTranslator
from src.utils.logger import logger
from src.utils.proxy import get_proxies


class BingTranslator(BaseTranslator):
    """Bing 翻译器"""
    
    def __init__(self):
        super().__init__("Bing")
        self.token_url = "https://edge.microsoft.com/translate/auth"
        self.api_url = "https://api-edge.cognitive.microsofttranslator.com/translate"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })
        
        # 获取代理配置
        self.proxies = get_proxies()
        if self.proxies:
            logger.info(f"[{self.name}] 已配置代理: {self.proxies}")
        
        logger.info(f"[{self.name}] 翻译器初始化成功")
    
    def _get_token(self) -> str:
        """
        获取 Bing Translate 认证 token
        
        Returns:
            token 字符串
        """
        try:
            response = self.session.get(
                self.token_url,
                proxies=self.proxies,
                timeout=10
            )
            response.raise_for_status()
            return response.text.strip()
        except Exception as e:
            logger.error(f"[{self.name}] 获取 token 失败: {e}")
            raise
    
    def translate(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "zh"
    ) -> Optional[str]:
        """
        使用 Bing Translate 翻译文本
        
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
            # 获取 token
            token = self._get_token()
            
            # 构建请求参数
            params = {
                "from": "" if source_lang == "auto" else source_lang,
                "to": target_lang,
                "api-version": "3.0",
            }
            
            # 构建请求头
            headers = {
                **self.session.headers,
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            
            # 构建请求体
            body = [{"Text": text}]
            
            # 发送请求
            response = self.session.post(
                self.api_url,
                params=params,
                json=body,
                headers=headers,
                proxies=self.proxies,
                timeout=12
            )
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            # 提取翻译结果
            translated_text = result[0]["translations"][0]["text"]
            logger.debug(f"[{self.name}] 翻译成功: {text[:50]}...")
            return translated_text.strip()
            
        except requests.RequestException as e:
            logger.error(f"[{self.name}] 网络请求失败: {e}")
            return None
        except Exception as e:
            logger.error(f"[{self.name}] 翻译失败: {e}", exc_info=True)
            return None