"""
数据模型定义

定义新闻数据的结构
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class NewsArticle(BaseModel):
    """新闻文章数据模型"""
    
    # 基本信息
    id: str = Field(description="新闻唯一标识")
    title: str = Field(description="原文标题")
    title_zh: str = Field(default="", description="中文标题")
    content: str = Field(description="原文内容")
    content_zh: str = Field(default="", description="中文内容")
    source: str = Field(description="新闻源名称")
    url: str = Field(description="新闻链接")
    published_at: datetime = Field(description="发布时间")
    fetched_at: datetime = Field(default_factory=datetime.now, description="抓取时间")
    
    # 分类信息
    category: str = Field(default="综合", description="新闻分类")
    priority: int = Field(default=5, ge=1, le=10, description="优先级 1-10")
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
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "abc123",
                "title": "Breaking News: Major Event",
                "title_zh": "突发新闻：重大事件",
                "content": "This is the news content...",
                "content_zh": "这是新闻内容...",
                "source": "Reuters",
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
