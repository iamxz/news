"""
LibreTranslate 翻译器

使用 LibreTranslate 公共实例进行翻译。
注意：大部分公共实例已关闭或需要 API key，此翻译器作为备用。
"""
import requests
import urllib3
from typing import Optional

from src.translators.base import BaseTranslator
from src.utils.logger import logger
from src.utils.proxy import get_proxies

# 禁用 SSL 警告（部分公共实例证书可能过期）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class LibreTranslator(BaseTranslator):
    """LibreTranslate 翻译器"""

    def __init__(self):
        super().__init__("LibreTranslate")
        # 更新镜像列表：旧的公共实例大多已失效
        # 如需可用，可在 .env 中设置 LIBRETRANSLATE_URL 自建实例
        self.mirrors = [
            "https://libretranslate.com",          # 需 API key，作为最后备选
            "https://translate.argosopentech.com",  # 时常不可用
            "https://libretranslate.de",            # 时常不可用
        ]

        # 支持自定义实例
        from src.utils.config import get_settings
        settings = get_settings()
        custom_url = getattr(settings, 'libretranslate_url', None)
        if custom_url:
            self.mirrors.insert(0, custom_url)
            self.api_key = getattr(settings, 'libretranslate_api_key', None)
        else:
            self.api_key = None

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
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
        target_lang: str = "zh",
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

        # LibreTranslate 语言代码映射
        lang_map = {
            "zh": "zh",
            "zh-cn": "zh",
            "zh-tw": "zh",
            "en": "en",
            "ja": "ja",
            "ko": "ko",
        }
        src = lang_map.get(source_lang, source_lang)
        tgt = lang_map.get(target_lang, target_lang)

        last_error = None
        for mirror in self.mirrors:
            try:
                url = f"{mirror}/translate"

                # 构建请求参数
                payload = {
                    "q": text,
                    "source": src if src != "auto" else "auto",
                    "target": tgt,
                    "format": "text",
                }
                if self.api_key:
                    payload["api_key"] = self.api_key

                # 发送请求（部分实例 SSL 证书可能过期，容忍 verify=False）
                response = self.session.post(
                    url,
                    json=payload,
                    proxies=self.proxies,
                    timeout=12,
                    verify=True,
                )
                response.raise_for_status()

                # 解析响应
                result = response.json()

                # 检查响应结构
                if "translatedText" not in result:
                    logger.warning(f"[{self.name}] 镜像 {mirror} 响应结构异常: {str(result)[:200]}")
                    continue

                # 提取翻译结果
                translated_text = result["translatedText"]
                logger.debug(f"[{self.name}] 翻译成功（镜像 {mirror}）: {text[:50]}...")
                return translated_text.strip()

            except requests.RequestException as e:
                logger.debug(f"[{self.name}] 镜像 {mirror} 请求失败: {e}")
                last_error = e
                continue
            except Exception as e:
                logger.debug(f"[{self.name}] 镜像 {mirror} 翻译失败: {e}")
                last_error = e
                continue

        logger.warning(f"[{self.name}] 所有镜像均失败: {last_error}")
        return None

    def is_available(self) -> bool:
        """
        检查 LibreTranslate 是否可用（至少一个镜像可达）。
        重写此方法以避免初始化时进行实际翻译测试。
        """
        # 如果配置了自定义实例，认为可用
        if self.mirrors and self.mirrors[0].startswith("https://") and self.api_key:
            return True
        # 公共实例大多已失效，标记为不可用以避免浪费时间
        # 如需启用，请在 .env 中配置 LIBRETRANSLATE_URL
        return False
