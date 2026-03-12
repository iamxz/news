"""
LibreTranslate 翻译器

使用 LibreTranslate 公共实例进行翻译
"""
from typing import Optional
import requests
import random

from src.translators.base import BaseTranslator
from src.utils.logger import logger
from src.utils.proxy import get_proxies


class LibreTranslator(BaseTranslator):
    """LibreTranslate 翻译器"""
    
    def __init__(self):
        super().__init__("LibreTranslate")
        self.mirrors = [
            "https://libretranslate.com",
            "https://translate.terraprint.co",
            "https://trans.zillyhuhn.com",
        ]
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Content-Type": "application/json",
        })
        
        # 获取代理配置
        self.proxies = get_proxies()
        if self.proxies:
            logger.info(f"[{self.name}] 已配置代理: {self.proxies}")
        
        logger.info(f"[{self.name}] 翻译器初始化成功")
    
    def translate(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "zh"
    ) -> Optional[str]:
        """
        使用 LibreTranslate 翻译文本
        
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
            # 随机选择一个镜像
            mirror = random.choice(self.mirrors)
            url = f"{mirror}/translate"
            
            # 构建请求参数
            payload = {
                "q": text,
                "source": source_lang if source_lang != "auto" else "auto",
                "target": target_lang,
                "format": "text",
            }
            
            # 发送请求
            response = self.session.post(
                url,
                json=payload,
                proxies=self.proxies,
                timeout=12
            )
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            # 检查响应结构
            if "translatedText" not in result:
                logger.error(f"[{self.name}] 响应结构异常: {result}")
                return None
            
            # 提取翻译结果
            translated_text = result["translatedText"]
            logger.debug(f"[{self.name}] 翻译成功: {text[:50]}...")
            return translated_text.strip()
            
        except requests.RequestException as e:
            logger.error(f"[{self.name}] 网络请求失败: {e}")
            return None
        except Exception as e:
            logger.error(f"[{self.name}] 翻译失败: {e}", exc_info=True)
            return None