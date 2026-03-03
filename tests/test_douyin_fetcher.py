"""测试抖音热榜抓取器"""
import asyncio
from src.fetchers.douyin import DouyinFetcher
from src.utils.logger import logger

async def test_douyin_fetcher():
    """测试抖音热榜抓取器"""
    logger.info("🧪 开始测试抖音热榜抓取器...")
    
    # 创建抖音热榜抓取器实例
    fetcher = DouyinFetcher()
    
    # 测试抓取功能
    logger.info(f"开始抓取 {fetcher.source_name}")
    articles = await fetcher.fetch()
    
    # 打印抓取结果
    logger.info(f"{fetcher.source_name} 抓取完成: {len(articles)} 条")
    
    # 打印前5条新闻
    if articles:
        logger.info("前5条抖音热榜:")
        for i, article in enumerate(articles[:5], 1):
            logger.info(f"{i}. {article.title}")
            logger.info(f"   链接: {article.url}")
            logger.info(f"   发布时间: {article.published_at}")
            logger.info(f"   可信度: {article.credibility_score}")
            logger.info("")
    else:
        logger.warning("未抓取到抖音热榜数据")

if __name__ == "__main__":
    asyncio.run(test_douyin_fetcher())
