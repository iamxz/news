"""
数据库操作模块

使用 SQLite 进行数据存储
"""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict

from src.storage.models import NewsArticle
from src.utils.config import get_settings
from src.utils.logger import logger


class Database:
    """数据库管理类"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        初始化数据库
        
        Args:
            db_path: 数据库文件路径
        """
        self.settings = get_settings()
        self.db_path = db_path or self.settings.database_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """初始化数据库表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建新闻表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    title_zh TEXT,
                    content TEXT,
                    content_zh TEXT,
                    source TEXT NOT NULL,
                    url TEXT NOT NULL,
                    published_at TIMESTAMP NOT NULL,
                    fetched_at TIMESTAMP NOT NULL,
                    category TEXT,
                    priority INTEGER,
                    tags TEXT,
                    credibility_score REAL,
                    fact_checked BOOLEAN,
                    cross_references INTEGER,
                    verification_labels TEXT,
                    warnings TEXT,
                    translated BOOLEAN DEFAULT 0,
                    validated BOOLEAN DEFAULT 0
                )
            """)
            
            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_published_at 
                ON articles(published_at DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_source 
                ON articles(source)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_category 
                ON articles(category)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_credibility 
                ON articles(credibility_score DESC)
            """)
            
            conn.commit()
            logger.info(f"数据库初始化完成: {self.db_path}")
    
    def save_article(self, article: NewsArticle) -> bool:
        """
        保存新闻文章
        
        Args:
            article: 新闻文章对象
        
        Returns:
            是否保存成功
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 将列表转换为 JSON 字符串
                import json
                tags_json = json.dumps(article.tags, ensure_ascii=False)
                labels_json = json.dumps(article.verification_labels, ensure_ascii=False)
                warnings_json = json.dumps(article.warnings, ensure_ascii=False)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO articles (
                        id, title, title_zh, content, content_zh, source, url,
                        published_at, fetched_at, category, priority, tags,
                        credibility_score, fact_checked,
                        cross_references, verification_labels, warnings,
                        translated, validated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article.id, article.title, article.title_zh,
                    article.content, article.content_zh, article.source, article.url,
                    article.published_at, article.fetched_at, article.category,
                    article.priority, tags_json, article.credibility_score,
                    article.fact_checked,
                    article.cross_references, labels_json, warnings_json,
                    article.translated, article.validated
                ))
                
                conn.commit()
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
        count = 0
        for article in articles:
            if self.save_article(article):
                count += 1
        
        logger.info(f"批量保存新闻: {count}/{len(articles)} 成功")
        return count
    
    def get_article(self, article_id: str) -> Optional[NewsArticle]:
        """
        根据 ID 获取新闻
        
        Args:
            article_id: 新闻 ID
        
        Returns:
            新闻对象，不存在则返回 None
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_article(row)
                return None
                
        except Exception as e:
            logger.error(f"获取新闻失败: {e}", exc_info=True)
            return None
    
    def get_articles(
        self,
        limit: int = 20,
        offset: int = 0,
        source: Optional[str] = None,
        category: Optional[str] = None,
        min_credibility: Optional[float] = None,
        days: Optional[int] = None
    ) -> List[NewsArticle]:
        """
        获取新闻列表
        
        Args:
            limit: 返回数量限制
            offset: 偏移量
            source: 筛选新闻源
            category: 筛选分类
            min_credibility: 最低可信度
            days: 最近几天的新闻
        
        Returns:
            新闻列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM articles WHERE 1=1"
                params = []
                
                if source:
                    query += " AND source = ?"
                    params.append(source)
                
                if category:
                    query += " AND category = ?"
                    params.append(category)
                
                if min_credibility is not None:
                    query += " AND credibility_score >= ?"
                    params.append(min_credibility)
                
                if days:
                    cutoff = datetime.now() - timedelta(days=days)
                    query += " AND published_at >= ?"
                    params.append(cutoff)
                
                query += " ORDER BY published_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [self._row_to_article(row) for row in rows]
                
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
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM articles 
                    WHERE translated = 0 
                    ORDER BY priority DESC, published_at DESC 
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                return [self._row_to_article(row) for row in rows]
                
        except Exception as e:
            logger.error(f"获取未翻译新闻失败: {e}", exc_info=True)
            return []
    
    def get_unvalidated_articles(self, limit: int = 10) -> List[NewsArticle]:
        """
        获取未验证的新闻
        
        Args:
            limit: 数量限制
        
        Returns:
            未验证的新闻列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM articles 
                    WHERE validated = 0 
                    ORDER BY priority DESC, published_at DESC 
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                return [self._row_to_article(row) for row in rows]
                
        except Exception as e:
            logger.error(f"获取未验证新闻失败: {e}", exc_info=True)
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
            cutoff = datetime.now() - timedelta(days=days)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM articles WHERE published_at < ?",
                    (cutoff,)
                )
                deleted = cursor.rowcount
                conn.commit()
                
                logger.info(f"删除 {days} 天前的旧新闻: {deleted} 条")
                return deleted
                
        except Exception as e:
            logger.error(f"删除旧新闻失败: {e}", exc_info=True)
            return 0
    
    def get_statistics(self) -> Dict:
        """
        获取数据库统计信息
        
        Returns:
            统计信息字典
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 总数
                cursor.execute("SELECT COUNT(*) FROM articles")
                total = cursor.fetchone()[0]
                
                # 按来源统计
                cursor.execute("""
                    SELECT source, COUNT(*) as count 
                    FROM articles 
                    GROUP BY source 
                    ORDER BY count DESC
                """)
                by_source = {row[0]: row[1] for row in cursor.fetchall()}
                
                # 翻译状态
                cursor.execute("SELECT COUNT(*) FROM articles WHERE translated = 1")
                translated = cursor.fetchone()[0]
                
                # 验证状态
                cursor.execute("SELECT COUNT(*) FROM articles WHERE validated = 1")
                validated = cursor.fetchone()[0]
                
                return {
                    'total': total,
                    'by_source': by_source,
                    'translated': translated,
                    'validated': validated
                }
                
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}", exc_info=True)
            return {}
    
    def count_articles(
        self,
        source: Optional[str] = None,
        category: Optional[str] = None,
        min_credibility: Optional[float] = None,
        days: Optional[int] = None
    ) -> int:
        """
        统计符合条件的新闻数量
        
        Args:
            source: 筛选新闻源
            category: 筛选分类
            min_credibility: 最低可信度
            days: 最近几天的新闻
        
        Returns:
            新闻数量
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = "SELECT COUNT(*) FROM articles WHERE 1=1"
                params = []
                
                if source:
                    query += " AND source = ?"
                    params.append(source)
                
                if category:
                    query += " AND category = ?"
                    params.append(category)
                
                if min_credibility is not None:
                    query += " AND credibility_score >= ?"
                    params.append(min_credibility)
                
                if days:
                    cutoff = datetime.now() - timedelta(days=days)
                    query += " AND published_at >= ?"
                    params.append(cutoff)
                
                cursor.execute(query, params)
                return cursor.fetchone()[0]
                
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
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT source FROM articles ORDER BY source")
                return [row[0] for row in cursor.fetchall()]
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
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT category FROM articles WHERE category IS NOT NULL ORDER BY category")
                return [row[0] for row in cursor.fetchall()]
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
    
    def _row_to_article(self, row: sqlite3.Row) -> NewsArticle:
        """
        将数据库行转换为 NewsArticle 对象
        
        Args:
            row: 数据库行
        
        Returns:
            NewsArticle 对象
        """
        import json
        
        return NewsArticle(
            id=row['id'],
            title=row['title'],
            title_zh=row['title_zh'] or '',
            content=row['content'] or '',
            content_zh=row['content_zh'] or '',
            source=row['source'],
            url=row['url'],
            published_at=datetime.fromisoformat(row['published_at']),
            fetched_at=datetime.fromisoformat(row['fetched_at']),
            category=row['category'] or '综合',
            priority=row['priority'] or 5,
            tags=json.loads(row['tags']) if row['tags'] else [],
            credibility_score=row['credibility_score'] or 0.0,
            fact_checked=bool(row['fact_checked']),
            cross_references=row['cross_references'] or 0,
            verification_labels=json.loads(row['verification_labels']) if row['verification_labels'] else [],
            warnings=json.loads(row['warnings']) if row['warnings'] else [],
            translated=bool(row['translated']),
            validated=bool(row['validated'])
        )


# 全局数据库实例
db = Database()
