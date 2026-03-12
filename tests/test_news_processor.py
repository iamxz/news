"""
新闻处理器测试
"""
import unittest
from datetime import datetime
from src.storage.models import NewsArticle
from src.utils import news_processor


class TestNewsProcessor(unittest.TestCase):
    """测试新闻处理器"""
    
    def setUp(self):
        """设置测试数据"""
        # 创建测试新闻
        self.article1 = NewsArticle(
            id="1",
            title="测试新闻标题 1",
            title_zh="Test News Title 1",
            content="这是测试新闻内容 1，包含一些测试信息。",
            content_zh="This is test news content 1, containing some test information.",
            source="test_source",
            url="https://example.com/news/1",
            published_at=datetime.now()
        )
        
        # 创建相似的新闻
        self.article2 = NewsArticle(
            id="2",
            title="测试新闻标题 1",
            title_zh="Test News Title 1",
            content="这是测试新闻内容 1，包含一些测试信息。",
            content_zh="This is test news content 1, containing some test information.",
            source="test_source",
            url="https://example.com/news/2",
            published_at=datetime.now()
        )
        
        # 创建不同的新闻
        self.article3 = NewsArticle(
            id="3",
            title="测试新闻标题 3",
            title_zh="Test News Title 3",
            content="这是测试新闻内容 3，包含不同的测试信息。",
            content_zh="This is test news content 3, containing different test information.",
            source="test_source",
            url="https://example.com/news/3",
            published_at=datetime.now()
        )
    
    def test_clean_article(self):
        """测试新闻清洗"""
        # 创建一个需要清洗的新闻
        dirty_article = NewsArticle(
            id="4",
            title="  测试新闻标题 4   ",
            title_zh="  Test News Title 4   ",
            content="  这是测试新闻内容 4，包含一些特殊字符！@#$%  ",
            content_zh="  This is test news content 4, containing some special characters!@#$%  ",
            source="test_source",
            url="https://example.com/news/4",
            published_at=datetime.now(),
            category="科技新闻",
            tags=["test", "news", "test"]  # 重复标签
        )
        
        # 清洗新闻
        cleaned_article = news_processor.clean_article(dirty_article)
        
        # 验证清洗结果
        self.assertEqual(cleaned_article.title, "测试新闻标题 4")
        self.assertEqual(cleaned_article.title_zh, "Test News Title 4")
        self.assertEqual(cleaned_article.content, "这是测试新闻内容 4，包含一些特殊字符！@#$%")
        self.assertEqual(cleaned_article.content_zh, "This is test news content 4, containing some special characters!@#$")
        self.assertEqual(cleaned_article.category, "科技")
        self.assertEqual(cleaned_article.tags, ["test", "news"])
    
    def test_calculate_similarity(self):
        """测试相似度计算"""
        # 计算相似新闻的相似度
        similarity1 = news_processor.calculate_similarity(
            self.article1.title, self.article2.title
        )
        self.assertGreater(similarity1, 0.9)
        
        # 计算不同新闻的相似度
        similarity2 = news_processor.calculate_similarity(
            self.article1.title, self.article3.title
        )
        self.assertLess(similarity2, 0.5)
    
    def test_group_similar_articles(self):
        """测试相似新闻分组"""
        articles = [self.article1, self.article2, self.article3]
        groups = news_processor.group_similar_articles(articles)
        
        # 应该分成两组：前两篇相似，第三篇不同
        self.assertEqual(len(groups), 2)
        self.assertEqual(len(groups[0]), 2)  # 相似新闻组
        self.assertEqual(len(groups[1]), 1)  # 不同新闻组
    
    def test_merge_similar_articles(self):
        """测试相似新闻合并"""
        # 设置不同的属性用于测试合并
        self.article1.credibility_score = 0.8
        self.article2.credibility_score = 0.9
        self.article1.tags = ["tag1"]
        self.article2.tags = ["tag2"]
        
        # 合并相似新闻
        merged_article = news_processor.merge_similar_articles([self.article1, self.article2])
        
        # 验证合并结果
        self.assertEqual(merged_article.id, self.article1.id)  # 使用最早的新闻 ID
        self.assertEqual(merged_article.credibility_score, 0.9)  # 取最高的可信度
        self.assertEqual(set(merged_article.tags), {"tag1", "tag2"})  # 合并标签
        self.assertEqual(merged_article.cross_references, 1)  # 交叉引用计数
        self.assertTrue(merged_article.validated)  # 标记为已验证
    
    def test_process_articles(self):
        """测试完整的新闻处理流程"""
        articles = [self.article1, self.article2, self.article3]
        processed_articles = news_processor.process_articles(articles)
        
        # 处理后应该有 2 篇新闻：前两篇合并，第三篇单独
        self.assertEqual(len(processed_articles), 2)


if __name__ == '__main__':
    unittest.main()
