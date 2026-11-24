"""
数据模型定义

定义新闻数据的结构
"""
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class NewsArticle(BaseModel):
    """新闻文章数据模型"""
    
    # 基本信息
    id: str = Field(description="新闻唯一标识")
    title: str = Field(description="原文标题")
    title_zh: str = Field(default="", description="中文标题")
    title_en: str = Field(default="", description="英文标题")
    content: str = Field(description="原文内容")
    content_zh: str = Field(default="", description="中文内容")
    content_en: str = Field(default="", description="英文内容")
    source: str = Field(description="新闻源名称")
    language: str = Field(default="en", description="原文语言代码")
    url: str = Field(description="新闻链接")
    published_at: datetime = Field(description="发布时间")
    fetched_at: datetime = Field(default_factory=datetime.now, description="抓取时间")
    
    # 分类信息
    category: str = Field(default="综合", description="新闻分类")
    priority: int = Field(default=5, ge=1, le=1000, description="优先级 1-100")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    
    # 翻译状态
    translated: bool = Field(default=False, description="是否已翻译")

    @classmethod
    def from_dict(cls, data: dict, fetcher=None) -> "NewsArticle":
        """
        从字典创建 NewsArticle，统一替代各处散落的手动转换逻辑。

        Args:
            data: 新闻字典数据
            fetcher: 可选的抓取器实例，用于补充 language 等默认值
        """
        # 优先使用字典中的 language，其次使用抓取器的 language
        default_lang = getattr(fetcher, 'language', 'en') if fetcher else 'en'
        language = data.get('language') or default_lang

        # 根据原文语言自动填充对应语言的字段
        title = data.get('title', '')
        content = data.get('content', '')
        title_zh = data.get('title_zh', '')
        title_en = data.get('title_en', '')
        content_zh = data.get('content_zh', '')
        content_en = data.get('content_en', '')

        # 如果尚未翻译，将原文填入对应语言字段
        translated = data.get('translated', False)
        if not translated:
            if language == 'zh':
                if not title_zh:
                    title_zh = title
                if not content_zh:
                    content_zh = content
            else:
                if not title_en:
                    title_en = title
                if not content_en:
                    content_en = content

        return cls(
            id=data.get('id'),
            title=title,
            title_zh=title_zh,
            title_en=title_en,
            content=content,
            content_zh=content_zh,
            content_en=content_en,
            source=data.get('source'),
            language=language,
            url=data.get('url'),
            published_at=data.get('published_at'),
            fetched_at=data.get('fetched_at', datetime.now()),
            category=data.get('category', '综合'),
            priority=data.get('priority', 5),
            tags=data.get('tags', []),
            translated=translated,
        )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "abc123",
                "title": "Breaking News: Major Event",
                "title_zh": "突发新闻：重大事件",
                "content": "This is the news content...",
                "content_zh": "这是新闻内容...",
                "source": "Reuters",
                "language": "en",
                "url": "https://example.com/news/1",
                "published_at": "2026-02-04T10:00:00",
                "category": "国际",
                "priority": 9,
                "tags": ["breaking", "politics"]
            }
        }
