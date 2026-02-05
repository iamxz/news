"""
配置管理模块

从环境变量和配置文件加载应用配置
"""
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


# 加载 .env 文件
load_dotenv()


class Settings(BaseSettings):
    """应用配置"""
    
    # API 密钥
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", alias="OPENAI_MODEL")
    deepl_api_key: str = Field(default="", alias="DEEPL_API_KEY")
    claude_api_key: str = Field(default="", alias="CLAUDE_API_KEY")
    
    # 百度翻译 API
    baidu_app_id: str = Field(default="", alias="BAIDU_APP_ID")
    baidu_secret_key: str = Field(default="", alias="BAIDU_SECRET_KEY")
    
    # 微软翻译 API
    microsoft_translator_key: str = Field(default="", alias="MICROSOFT_TRANSLATOR_KEY")
    microsoft_translator_region: str = Field(default="global", alias="MICROSOFT_TRANSLATOR_REGION")
    
    # Reddit API
    reddit_client_id: str = Field(default="", alias="REDDIT_CLIENT_ID")
    reddit_client_secret: str = Field(default="", alias="REDDIT_CLIENT_SECRET")
    reddit_user_agent: str = Field(
        default="NewsAggregator/1.0",
        alias="REDDIT_USER_AGENT"
    )
    
    # 数据库
    database_path: Path = Field(
        default=Path("./data/news.db"),
        alias="DATABASE_PATH"
    )
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")
    
    # 抓取配置
    fetch_interval: str = Field(default="6h", alias="FETCH_INTERVAL")
    max_news_per_source: int = Field(default=20, alias="MAX_NEWS_PER_SOURCE")
    news_retention_days: int = Field(default=30, alias="NEWS_RETENTION_DAYS")
    user_agent: str = Field(
        default="NewsAggregator/1.0 (+https://github.com/yourname/news)",
        alias="USER_AGENT"
    )
    
    # 验证配置
    enable_credibility_check: bool = Field(default=True, alias="ENABLE_CREDIBILITY_CHECK")
    enable_fact_check: bool = Field(default=True, alias="ENABLE_FACT_CHECK")
    min_credibility_threshold: float = Field(default=0.5, alias="MIN_CREDIBILITY_THRESHOLD")
    cross_ref_search_enabled: bool = Field(default=True, alias="CROSS_REF_SEARCH_ENABLED")
    
    # 代理配置
    http_proxy: Optional[str] = Field(default=None, alias="HTTP_PROXY")
    https_proxy: Optional[str] = Field(default=None, alias="HTTPS_PROXY")
    
    # 日志配置
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings
