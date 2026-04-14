"""
JSON 存储模块

使用 JSON 文件进行数据存储，按时间进行存放
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Tuple

from src.storage.models import NewsArticle
from src.utils.config import get_settings
from src.utils.logger import logger


class JSONStorage:
    """JSON 存储管理类"""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        初始化 JSON 存储
        
        Args:
            storage_dir: 存储目录路径
        """
        self.settings = get_settings()
        self.storage_dir = storage_dir or self.settings.json_storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.current_file = self._get_current_file()
    
    def _get_current_file(self) -> Path:
        """
        获取当前日期的 JSON 文件路径
        
        Returns:
            当前日期的 JSON 文件路径
        """
        today = datetime.now().strftime('%Y-%m-%d')
        return self.storage_dir / f"news_{today}.json"
    
    def _read_articles(self) -> List[Dict]:
        """
        从当前 JSON 文件读取新闻
        
        Returns:
            新闻列表
        """
        if not self.current_file.exists():
            return []
        
        try:
            with open(self.current_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取 JSON 文件失败: {e}")
            return []
    
    def _write_articles(self, articles: List[Dict]):
        """
        将新闻写入当前 JSON 文件
        
        Args:
            articles: 新闻列表
        """
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"成功写入 {len(articles)} 篇新闻到 {self.current_file}")
        except Exception as e:
            logger.error(f"写入 JSON 文件失败: {e}")
    
    def save_article(self, article: NewsArticle) -> bool:
        """
        保存新闻文章
        
        Args:
            article: 新闻文章对象
        
        Returns:
            是否保存成功
        """
        try:
            articles = self._read_articles()
            article_dict = article.dict()
            
            # 检查是否已存在相同 ID 的新闻
            existing_index = next((i for i, a in enumerate(articles) if a['id'] == article.id), -1)
            
            if existing_index >= 0:
                # 更新已存在的新闻
                articles[existing_index] = article_dict
            else:
                # 添加新新闻
                articles.append(article_dict)
            
            self._write_articles(articles)
            logger.debug(f"保存新闻: {article.title[:50]}")
            return True
            
        except Exception as e:
            logger.error(f"保存新闻失败: {e}", exc_info=True)
            return False
    
    def save_articles(self, articles: List[NewsArticle]) -> int:
        """
        批量保存新闻

        Args:
            articles: 新闻列表

        Returns:
            成功保存的数量
        """
        if not articles:
            return 0

        count = 0
        try:
            existing_articles = self._read_articles()
            existing_ids = {a['id'] for a in existing_articles}
            new_articles = []
            
            for article in articles:
                try:
                    article_dict = article.dict()
                    if article.id not in existing_ids:
                        new_articles.append(article_dict)
                        count += 1
                except Exception as e:
                    logger.error(f"批量保存中单条失败: {e}")
            
            # 清空现有数据，只保留新抓取的新闻
            all_articles = new_articles
            self._write_articles(all_articles)
            
            logger.info(f"批量保存新闻: {count}/{len(articles)} 成功")
            return count
        except Exception as e:
            logger.error(f"批量保存新闻失败: {e}", exc_info=True)
            return 0
    
    def get_article(self, article_id: str) -> Optional[NewsArticle]:
        """
        根据 ID 获取新闻
        
        Args:
            article_id: 新闻 ID
        
        Returns:
            新闻对象，不存在则返回 None
        """
        try:
            articles = self._read_articles()
            for article_dict in articles:
                if article_dict['id'] == article_id:
                    return NewsArticle.from_dict(article_dict)
            return None
            
        except Exception as e:
            logger.error(f"获取新闻失败: {e}", exc_info=True)
            return None
    
    def get_articles(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        source: Optional[str] = None,
        category: Optional[str] = None,
        min_credibility: Optional[float] = None
    ) -> List[NewsArticle]:
        """
        获取新闻列表

        Args:
            limit: 返回数量限制，None 表示不限制
            offset: 偏移量
            source: 筛选新闻源
            category: 筛选分类
            min_credibility: 最低可信度

        Returns:
            新闻列表
        """
        try:
            articles = self._read_articles()
            
            # 过滤
            filtered_articles = []
            for article_dict in articles:
                if source and article_dict.get('source') != source:
                    continue
                if category and article_dict.get('category') != category:
                    continue
                if min_credibility is not None and article_dict.get('credibility_score', 0) < min_credibility:
                    continue
                filtered_articles.append(article_dict)
            
            # 排序：优先按优先级，然后按发布时间
            filtered_articles.sort(key=lambda x: (-x.get('priority', 5), -datetime.fromisoformat(x['published_at']).timestamp()))
            
            # 分页
            if limit is not None:
                filtered_articles = filtered_articles[offset:offset + limit]
            else:
                filtered_articles = filtered_articles[offset:]
            
            # 转换为 NewsArticle 对象
            result = []
            for article_dict in filtered_articles:
                try:
                    article = NewsArticle.from_dict(article_dict)
                    result.append(article)
                except Exception as e:
                    logger.error(f"转换新闻对象失败: {e}")
            
            logger.info(f"查询结果数量: {len(result)}")
            return result
        except Exception as e:
            logger.error(f"获取新闻列表失败: {e}", exc_info=True)
            return []
    
    def get_untranslated_articles(self, limit: int = 10) -> List[NewsArticle]:
        """
        获取未翻译的新闻
        
        Args:
            limit: 数量限制
        
        Returns:
            未翻译的新闻列表
        """
        try:
            articles = self._read_articles()
            untranslated = []
            
            for article_dict in articles:
                if not article_dict.get('translated', False):
                    try:
                        article = NewsArticle.from_dict(article_dict)
                        untranslated.append(article)
                    except Exception as e:
                        logger.error(f"转换新闻对象失败: {e}")
            
            # 排序并限制数量
            untranslated.sort(key=lambda x: (-x.priority, -x.published_at.timestamp()))
            return untranslated[:limit]
            
        except Exception as e:
            logger.error(f"获取未翻译新闻失败: {e}", exc_info=True)
            return []
    
    def delete_old_articles(self, days: int = 30) -> int:
        """
        删除旧新闻
        
        Args:
            days: 保留最近多少天的新闻
        
        Returns:
            删除的数量
        """
        try:
            deleted = 0
            cutoff_date = (datetime.now() - timedelta(days=days)).date()
            
            for file_path in self.storage_dir.glob("news_*.json"):
                try:
                    file_date_str = file_path.stem.replace("news_", "")
                    file_date = datetime.strptime(file_date_str, "%Y-%m-%d").date()
                    
                    if file_date < cutoff_date:
                        file_path.unlink()
                        deleted += 1
                except Exception as e:
                    logger.error(f"删除旧文件失败: {e}")
            
            logger.info(f"删除 {days} 天前的旧新闻文件: {deleted} 个")
            return deleted
            
        except Exception as e:
            logger.error(f"删除旧新闻失败: {e}", exc_info=True)
            return 0
    
    def delete_all_articles(self) -> int:
        """
        删除所有新闻
        
        Returns:
            删除的数量
        """
        try:
            if self.current_file.exists():
                articles = self._read_articles()
                deleted_count = len(articles)
                self._write_articles([])
                logger.info(f"删除所有新闻: {deleted_count} 条")
                return deleted_count
            return 0
            
        except Exception as e:
            logger.error(f"删除所有新闻失败: {e}", exc_info=True)
            return 0
    
    def get_statistics(self) -> Dict:
        """
        获取存储统计信息
        
        Returns:
            统计信息字典
        """
        try:
            articles = self._read_articles()
            
            # 总数
            total = len(articles)
            
            # 按来源统计
            by_source = {}
            for article in articles:
                source = article.get('source', '未知')
                by_source[source] = by_source.get(source, 0) + 1
            
            # 翻译状态
            translated = sum(1 for article in articles if article.get('translated', False))
            
            return {
                'total': total,
                'by_source': by_source,
                'translated': translated
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}", exc_info=True)
            return {}
    
    def count_articles(
        self,
        source: Optional[str] = None,
        category: Optional[str] = None,
        min_credibility: Optional[float] = None
    ) -> int:
        """
        统计符合条件的新闻数量

        Args:
            source: 筛选新闻源
            category: 筛选分类
            min_credibility: 最低可信度

        Returns:
            新闻数量
        """
        try:
            articles = self._read_articles()
            count = 0
            
            for article_dict in articles:
                if source and article_dict.get('source') != source:
                    continue
                if category and article_dict.get('category') != category:
                    continue
                if min_credibility is not None and article_dict.get('credibility_score', 0) < min_credibility:
                    continue
                count += 1
            
            return count
        except Exception as e:
            logger.error(f"统计新闻数量失败: {e}", exc_info=True)
            return 0
    
    def get_all_sources(self) -> List[str]:
        """
        获取所有新闻源
        
        Returns:
            新闻源列表
        """
        try:
            articles = self._read_articles()
            sources = {article.get('source') for article in articles if article.get('source')}
            return sorted(sources)
        except Exception as e:
            logger.error(f"获取新闻源列表失败: {e}", exc_info=True)
            return []
    
    def get_all_categories(self) -> List[str]:
        """
        获取所有分类
        
        Returns:
            分类列表
        """
        try:
            articles = self._read_articles()
            categories = {article.get('category') for article in articles if article.get('category')}
            return sorted(categories)
        except Exception as e:
            logger.error(f"获取分类列表失败: {e}", exc_info=True)
            return []
    
    def get_article_by_id(self, article_id: str) -> Optional[NewsArticle]:
        """
        根据 ID 获取新闻（别名方法）
        
        Args:
            article_id: 新闻 ID
        
        Returns:
            新闻对象
        """
        return self.get_article(article_id)


# 全局 JSON 存储实例
json_db = JSONStorage()
