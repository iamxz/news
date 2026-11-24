"""
Google 翻译器

使用 requests 直接调用 Google Translate API（免费的 Web 接口）
"""
from typing import Optional
import requests
import json
import random
import time

from src.translators.base import BaseTranslator
from src.utils.logger import logger


class GoogleTranslator(BaseTranslator):
    """Google 翻译器（使用免费 API）"""
    
    def __init__(self):
        super().__init__("Google Translate")
        
        # Google Translate API 免费接口
        # client=at 比 client=gtx 更不容易被 429 限流
        self.api_url = "https://translate.googleapis.com/translate_a/single"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # 获取代理配置
        from src.utils.proxy import get_proxies
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
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Google 语言代码映射
                lang_map = {
                    "zh": "zh-CN",
                    "zh-cn": "zh-CN",
                    "zh-tw": "zh-TW",
                    "en": "en",
                    "ja": "ja",
                    "ko": "ko",
                }
                src = lang_map.get(source_lang, source_lang)
                tgt = lang_map.get(target_lang, target_lang)

                # Google Translate 参数
                # client=at 比 gtx 限流更少；交替使用以分散风险
                client = 'at' if attempt % 2 == 0 else 'gtx'
                params = {
                    'client': client,
                    'sl': src,  # 源语言
                    'tl': tgt,  # 目标语言
                    'dt': 't',  # 翻译文本
                    'q': text  # 要翻译的文本
                }
                
                # 发送请求
                response = self.session.get(
                    self.api_url,
                    params=params,
                    proxies=self.proxies,
                    timeout=10
                )
                
                # 检查是否是 429 错误
                if response.status_code == 429:
                    wait = retry_delay * (2 ** attempt) + random.uniform(1, 3)
                    logger.warning(f"[{self.name}] 请求过于频繁 ({attempt+1}/{max_retries})，等待 {wait:.1f}s 后重试 (client={client})...")
                    time.sleep(wait)
                    continue
                
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
                if "429" in str(e):
                    logger.warning(f"[{self.name}] 请求过于频繁，正在重试 ({attempt+1}/{max_retries})...")
                    time.sleep(retry_delay * (2 ** attempt))  # 指数退避
                    continue
                logger.error(f"[{self.name}] 网络请求失败: {e}")
                return None
            except json.JSONDecodeError as e:
                logger.error(f"[{self.name}] JSON 解析失败: {e}")
                return None
            except Exception as e:
                logger.error(f"[{self.name}] 翻译失败: {e}", exc_info=True)
                return None
        
        logger.error(f"[{self.name}] 多次尝试后仍然失败")
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
                time.sleep(random.uniform(1, 3))  # 随机延迟，避免429错误
        
        return results
