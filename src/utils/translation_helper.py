"""
翻译辅助模块

统一管理语言来源常量和文章翻译逻辑，避免在多处重复相同代码。
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.storage.models import NewsArticle
    from src.translators import TranslatorManager

# 各语系新闻源常量（集中维护，避免散落在各处硬编码）
JAPANESE_SOURCES = frozenset([
    'NHK World', 'Asahi Shimbun', 'The Japan Times', 'Mainichi'
])
CHINESE_SOURCES = frozenset([
    '今日头条', '百度热搜', '微博热搜', '联合早报',
    '8视界', '新明日报', '南华早报', '端传媒'
])


def detect_source_lang(source: str) -> str:
    """
    根据新闻来源名称推断原文语言。

    Returns:
        'ja' | 'zh' | 'en'
    """
    if source in JAPANESE_SOURCES:
        return 'ja'
    if source in CHINESE_SOURCES:
        return 'zh'
    return 'en'


def translate_article(article: "NewsArticle", translator_manager: "TranslatorManager") -> None:
    """
    就地补全文章的多语言字段，跳过已有内容，不重复翻译。

    根据来源语言决定翻译方向：
    - 日文源：ja -> zh, ja -> en
    - 中文源：原文作为 zh，zh -> en
    - 英文源（默认）：原文作为 en，en -> zh

    Args:
        article: 待翻译的 NewsArticle 对象（原地修改）
        translator_manager: 翻译管理器实例
    """
    source_lang = detect_source_lang(article.source)

    def _translate(text: str, src: str, tgt: str) -> str:
        """若文本非空则翻译，否则返回空字符串。"""
        if not text:
            return ''
        return translator_manager.translate(text, source_lang=src, target_lang=tgt) or ''

    if source_lang == 'ja':
        # 日文 -> 中文 / 英文
        if not article.title_en:
            article.title_en = _translate(article.title, 'ja', 'en')
        if not article.title_zh:
            article.title_zh = _translate(article.title, 'ja', 'zh')
        if not article.content_en:
            article.content_en = _translate(article.content, 'ja', 'en')
        if not article.content_zh:
            article.content_zh = _translate(article.content, 'ja', 'zh')

    elif source_lang == 'zh':
        # 中文原文直接作为 zh 字段，只需翻译成英文
        if not article.title_zh:
            article.title_zh = article.title
        if not article.title_en:
            article.title_en = _translate(article.title, 'zh', 'en')
        if not article.content_zh:
            article.content_zh = article.content
        if not article.content_en:
            article.content_en = _translate(article.content, 'zh', 'en')

    else:
        # 英文原文直接作为 en 字段，只需翻译成中文
        if not article.title_en:
            article.title_en = article.title
        if not article.title_zh:
            article.title_zh = _translate(article.title, 'en', 'zh')
        if not article.content_en:
            article.content_en = article.content
        if not article.content_zh:
            article.content_zh = _translate(article.content, 'en', 'zh')

    article.translated = True
