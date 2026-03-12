"""
翻译器管理模块

管理和选择可用的翻译器
"""
from typing import Optional

from src.translators.base import BaseTranslator
from src.translators.google import GoogleTranslator
from src.utils.logger import logger

# 暂时禁用 FreeTranslator 以避免依赖冲突
FREE_TRANSLATOR_AVAILABLE = False


class TranslatorManager:
    """翻译器管理器"""
    
    def __init__(self):
        """初始化翻译器管理器"""
        self.translators = []
        self._init_translators()
    
    def _init_translators(self):
        """初始化所有可用的翻译器"""
        # 按优先级顺序添加翻译器（真正免费的在前）
        translators = []
        
        # 添加 Google 翻译（免费，无需 API key）
        try:
            translators.append(GoogleTranslator())
        except Exception as e:
            logger.warning(f"Google 翻译器初始化失败: {e}")
        
        # 尝试添加 Bing 翻译（免费，无需 API key）
        try:
            from src.translators.bing import BingTranslator
            translators.append(BingTranslator())
        except Exception as e:
            logger.warning(f"Bing 翻译器初始化失败: {e}")
        
        # 尝试添加 MyMemory 翻译（免费，无需 API key）
        try:
            from src.translators.mymemory import MyMemoryTranslator
            translators.append(MyMemoryTranslator())
        except Exception as e:
            logger.warning(f"MyMemory 翻译器初始化失败: {e}")
        
        # 尝试添加 LibreTranslate 翻译（免费，无需 API key）
        try:
            from src.translators.libre import LibreTranslator
            translators.append(LibreTranslator())
        except Exception as e:
            logger.warning(f"LibreTranslate 翻译器初始化失败: {e}")
        
        # 尝试添加百度翻译（需要 API key）
        try:
            from src.translators.baidu import BaiduTranslator
            translators.append(BaiduTranslator())
        except Exception as e:
            logger.warning(f"百度翻译器初始化失败: {e}")
        
        # 尝试添加微软翻译（需要 API key）
        try:
            from src.translators.microsoft import MicrosoftTranslator
            translators.append(MicrosoftTranslator())
        except Exception as e:
            logger.warning(f"微软翻译器初始化失败: {e}")
        
        # 尝试添加 DeepL 翻译（需要 API key）
        try:
            from src.translators.deepl import DeepLTranslator
            translators.append(DeepLTranslator())
        except Exception as e:
            logger.warning(f"DeepL 翻译器初始化失败: {e}")
        
        # 尝试添加 OpenAI 翻译（需要 API key）
        try:
            from src.translators.openai import OpenAITranslator
            translators.append(OpenAITranslator())
        except Exception as e:
            logger.warning(f"OpenAI 翻译器初始化失败: {e}")
        
        for translator in translators:
            try:
                # 检查翻译器是否可以使用
                if hasattr(translator, 'translator') and translator.translator is None:
                    # 特别检查 FreeTranslator 的情况
                    if translator.__class__.__name__ == 'FreeTranslator':
                        if not hasattr(translator, 'translator') or translator.translator is None:
                            logger.debug(f"翻译器跳过 ({translator.name}): 依赖库未安装或初始化失败")
                            continue
                
                # 对于免费翻译器（不需要 API key），直接加载
                free_translators = ['GoogleTranslator', 'BingTranslator', 'MyMemoryTranslator', 'LibreTranslator']
                if translator.__class__.__name__ in free_translators:
                    self.translators.append(translator)
                    logger.info(f"翻译器已加载: {translator.name}")
                else:
                    # 检查其他翻译器是否有有效的客户端
                    has_client = (
                        hasattr(translator, 'client') and translator.client is not None
                    ) or (
                        hasattr(translator, 'translator') and translator.translator is not None
                    ) or (
                        hasattr(translator, 'session') and translator.session is not None
                    )
                    
                    if has_client:
                        self.translators.append(translator)
                        logger.info(f"翻译器已加载: {translator.name}")
                    else:
                        logger.debug(f"翻译器跳过 ({translator.name}): API key 未配置或初始化失败")
            except Exception as e:
                logger.warning(f"翻译器初始化失败 ({translator.name}): {e}")
        
        if not self.translators:
            logger.error("没有可用的翻译器！请检查 API 配置")
    
    def get_translator(self) -> Optional[BaseTranslator]:
        """
        获取第一个可用的翻译器
        
        Returns:
            翻译器实例，如果没有可用的返回 None
        """
        for translator in self.translators:
            if translator.is_available():
                return translator
        
        logger.error("没有可用的翻译器")
        return None
    
    def translate(self, text: str, source_lang: str = "en", target_lang: str = "zh") -> Optional[str]:
        """
        翻译文本（自动选择可用的翻译器）
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言
            target_lang: 目标语言
        
        Returns:
            翻译结果
        """
        if not text or not text.strip():
            return ""
        
        # 尝试使用每个翻译器
        for translator in self.translators:
            try:
                logger.info(f"尝试使用翻译器: {translator.name}")
                result = translator.translate(text, source_lang, target_lang)
                if result:
                    logger.info(f"翻译完成: {text[:50]}")
                    return result
                else:
                    logger.warning(f"翻译器 {translator.name} 返回空结果，正在尝试下一个翻译器...")
            except Exception as e:
                logger.warning(f"翻译器 {translator.name} 失败: {e}，正在尝试下一个翻译器...")
                continue
        
        logger.error(f"所有翻译器都失败了: {text[:50]}")
        return None


# 全局翻译管理器实例
translator_manager = TranslatorManager()
