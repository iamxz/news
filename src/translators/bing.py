"""
Bing 翻译器

使用 Bing Translate 网页接口进行翻译。
旧端点 edge.microsoft.com/translate/auth 已失效（404），
改用 www.bing.com/ttranslatev3 端点。
"""
import re
import time
import random
from typing import Optional

import requests

from src.translators.base import BaseTranslator
from src.utils.logger import logger
from src.utils.proxy import get_proxies


class BingTranslator(BaseTranslator):
    """Bing 翻译器（使用 www.bing.com/ttranslatev3 端点）"""

    def __init__(self):
        super().__init__("Bing")
        self.translator_url = "https://www.bing.com/translator"
        self.api_url = "https://www.bing.com/ttranslatev3"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })

        # 获取代理配置
        self.proxies = get_proxies()
        if self.proxies:
            logger.info(f"[{self.name}] 已配置代理: {self.proxies}")

        # 页面 token 缓存
        self._ig: Optional[str] = None
        self._iid: str = "translator.5023"
        self._token_time: float = 0
        self._token_ttl: int = 3000  # token 有效期约 50 分钟

        logger.info(f"[{self.name}] 翻译器初始化成功")

    def _refresh_page_tokens(self) -> bool:
        """
        访问 Bing 翻译页面，获取 IG token 和 cookie。

        Returns:
            是否成功获取 token
        """
        try:
            r = self.session.get(
                self.translator_url,
                proxies=self.proxies,
                timeout=10,
            )
            r.raise_for_status()

            ig = re.search(r'IG:"([^"]+)"', r.text)
            iid = re.search(r'data-iid="([^"]+)"', r.text)

            if ig:
                self._ig = ig.group(1)
            if iid:
                self._iid = iid.group(1)

            if self._ig:
                self._token_time = time.time()
                logger.debug(f"[{self.name}] 页面 token 刷新成功: IG={self._ig[:16]}...")
                return True

            logger.warning(f"[{self.name}] 未能从页面提取 IG token")
            return False

        except Exception as e:
            logger.warning(f"[{self.name}] 刷新页面 token 失败: {e}")
            return False

    def _ensure_tokens(self) -> bool:
        """确保 token 有效，过期则刷新"""
        if self._ig and (time.time() - self._token_time < self._token_ttl):
            return True
        return self._refresh_page_tokens()

    def translate(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "zh",
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

        # Bing 语言代码映射
        lang_map = {
            "zh": "zh-Hans",
            "zh-cn": "zh-Hans",
            "zh-tw": "zh-Hant",
            "en": "en",
            "ja": "ja",
            "ko": "ko",
        }
        src = lang_map.get(source_lang, source_lang)
        tgt = lang_map.get(target_lang, target_lang)

        max_retries = 2
        for attempt in range(max_retries):
            if not self._ensure_tokens():
                logger.warning(f"[{self.name}] 无法获取页面 token，重试 ({attempt+1}/{max_retries})")
                time.sleep(random.uniform(1, 2))
                continue

            try:
                url = (
                    f"{self.api_url}?isVertical=1"
                    f"&IG={self._ig}&IID={self._iid}"
                )

                payload = {
                    "text": text,
                    "fromLang": src,
                    "to": tgt,
                    "tryAttemptGeography": True,
                }

                headers = {
                    "User-Agent": self.session.headers["User-Agent"],
                    "Accept": "application/json",
                    "Content-Type": "application/json; charset=UTF-8",
                    "Referer": self.translator_url,
                    "Origin": "https://www.bing.com",
                }

                response = self.session.post(
                    url,
                    json=payload,
                    headers=headers,
                    proxies=self.proxies,
                    timeout=12,
                )
                response.raise_for_status()

                # 检查是否有有效内容
                if not response.text or len(response.text) == 0:
                    # 空 body，刷新 token 后重试
                    logger.warning(f"[{self.name}] 响应为空，刷新 token 后重试 ({attempt+1}/{max_retries})")
                    self._ig = None
                    time.sleep(random.uniform(1, 2))
                    continue

                result = response.json()

                # 检查 statusCode（205 表示被反爬拦截）
                status_code = result.get("statusCode")
                if status_code and status_code != 200:
                    logger.warning(
                        f"[{self.name}] 翻译被拦截 (statusCode={status_code})，"
                        f"刷新 token 后重试 ({attempt+1}/{max_retries})"
                    )
                    self._ig = None
                    time.sleep(random.uniform(2, 4))
                    continue

                # 提取翻译结果
                # 正常响应格式: [{"translations": [{"text": "翻译结果"}]}]
                if isinstance(result, list) and len(result) > 0:
                    translated_text = result[0].get("translations", [{}])[0].get("text", "")
                    if translated_text:
                        logger.debug(f"[{self.name}] 翻译成功: {text[:50]}...")
                        return translated_text.strip()

                logger.warning(f"[{self.name}] 响应结构异常: {str(result)[:200]}")
                return None

            except requests.RequestException as e:
                logger.warning(f"[{self.name}] 网络请求失败: {e}")
                self._ig = None
                time.sleep(random.uniform(1, 2))
                continue
            except Exception as e:
                logger.warning(f"[{self.name}] 翻译失败: {e}")
                self._ig = None
                continue

        logger.error(f"[{self.name}] 多次尝试后仍然失败")
        return None
