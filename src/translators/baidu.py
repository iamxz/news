"""
百度翻译器

使用百度翻译 API（免费额度）
"""
from typing import Optional
import hashlib
import requests
import random
import time

from src.translators.base import BaseTranslator
from src.utils.config import get_settings
from src.utils.logger import logger


class BaiduTranslator(BaseTranslator):
    """百度翻译器"""
    
    API_URL = "https://fanyi-api.baidu.com/api/trans/vip/translate"
    
    def __init__(self):
        super().__init__("百度翻译")
        self.settings = get_settings()
        
        # 从环境变量获取 APP ID 和密钥
        self.app_id = getattr(self.settings, 'baidu_app_id', None)
        self.secret_key = getattr(self.settings, 'baidu_secret_key', None)
        
        if not self.app_id or not self.secret_key:
            logger.warning(f"[{self.name}] 百度翻译 APP ID 或密钥未配置")
            self.translator = None
        else:
            self.translator = True  # 标记已初始化
            logger.info(f"[{self.name}] 翻译器初始化成功")
    
    def _generate_sign(self, query: str, salt: str) -> str:
        """
        生成百度翻译 API 签名
        
        Args:
            query: 要翻译的文本
            salt: 随机数
        
        Returns:
            签名字符串
        """
        sign_str = f"{self.app_id}{query}{salt}{self.secret_key}"
        md5 = hashlib.md5()
        md5.update(sign_str.encode('utf-8'))
        return md5.hexdigest()
    
    def translate(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "zh"
    ) -> Optional[str]:
        """
        使用百度翻译 API 翻译文本
        
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
            # 百度翻译语言代码
            lang_map = {
                "en": "en",
                "zh": "zh",
                "ja": "jp",
                "ko": "kor",
                "fr": "fra",
                "de": "de",
                "es": "spa",
                "ru": "ru",
            }
            
            from_lang = lang_map.get(source_lang, "auto")
            to_lang = lang_map.get(target_lang, "zh")
            
            # 生成随机数和签名
            salt = str(random.randint(32768, 65536))
            sign = self._generate_sign(text, salt)
            
            # 构建请求参数
            params = {
                'q': text,
                'from': from_lang,
                'to': to_lang,
                'appid': self.app_id,
                'salt': salt,
                'sign': sign
            }
            
            # 发送请求
            response = requests.get(self.API_URL, params=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            # 检查错误
            if 'error_code' in result:
                error_code = result['error_code']
                error_msg = result.get('error_msg', '未知错误')
                logger.error(f"[{self.name}] API 错误 {error_code}: {error_msg}")
                return None
            
            # 提取翻译结果
            if 'trans_result' in result and len(result['trans_result']) > 0:
                translation = result['trans_result'][0]['dst']
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
        批量翻译
        
        Args:
            texts: 文本列表
            source_lang: 源语言代码
            target_lang: 目标语言代码
        
        Returns:
            翻译结果列表
        """
        if not self.translator:
            return [None] * len(texts)
        
        results = []
        for i, text in enumerate(texts):
            result = self.translate(text, source_lang, target_lang)
            results.append(result)
            
            # 百度翻译 API QPS 限制为 10 次/秒
            if i < len(texts) - 1:
                time.sleep(0.2)
        
        return results
