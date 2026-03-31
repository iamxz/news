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
    
    # 验证信息
    credibility_score: float = Field(default=0.0, ge=0.0, le=1.0, description="可信度评分")
    fact_checked: bool = Field(default=False, description="是否经过事实核查")
    cross_references: int = Field(default=0, ge=0, description="交叉引用数量")
    verification_labels: List[str] = Field(default_factory=list, description="验证标签")
    warnings: List[str] = Field(default_factory=list, description="警告信息")
    
    # 翻译状态
    translated: bool = Field(default=False, description="是否已翻译")
    validated: bool = Field(default=False, description="是否已验证")
    
    @classmethod
    def from_dict(cls, data: dict, fetcher=None) -> "NewsArticle":
        """
        从字典创建 NewsArticle，统一替代各处散落的手动转换逻辑。

        Args:
            data: 新闻字典数据
            fetcher: 可选的抓取器实例，用于补充 language 等默认值
        """
        default_lang = getattr(fetcher, 'language', 'en') if fetcher else 'en'
        return cls(
            id=data.get('id'),
            title=data.get('title'),
            title_zh=data.get('title_zh', ''),
            title_en=data.get('title_en', ''),
            content=data.get('content'),
            content_zh=data.get('content_zh', ''),
            content_en=data.get('content_en', ''),
            source=data.get('source'),
            language=data.get('language', default_lang),
            url=data.get('url'),
            published_at=data.get('published_at'),
            fetched_at=data.get('fetched_at', datetime.now()),
            category=data.get('category', '综合'),
            priority=data.get('priority', 5),
            tags=data.get('tags', []),
            credibility_score=data.get('credibility_score', 0.0),
            fact_checked=data.get('fact_checked', False),
            cross_references=data.get('cross_references', 0),
            verification_labels=data.get('verification_labels', []),
            warnings=data.get('warnings', []),
            translated=data.get('translated', False),
            validated=data.get('validated', False),
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
                "tags": ["breaking", "politics"],
                "credibility_score": 0.95,
                "bias_rating": "neutral",
                "bias_score": 0.15,
                "fact_checked": True,
                "cross_references": 5,
                "verification_labels": ["高可信度", "客观报道"],
                "warnings": []
            }
        }


class SourceCredibility(BaseModel):
    """新闻源可信度模型"""
    
    source_name: str = Field(description="新闻源名称")
    base_credibility: float = Field(ge=0.0, le=1.0, description="基础可信度")
    bias_tendency: str = Field(default="neutral", description="偏见倾向")
    category: str = Field(description="媒体类型")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_name": "Reuters",
                "base_credibility": 0.95,
                "bias_tendency": "neutral",
                "category": "通讯社"
            }
        }
