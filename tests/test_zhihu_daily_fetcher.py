"""测试知乎日报抓取器"""
import asyncio
from src.fetchers import ZhihuDailyFetcher
from src.utils.logger import logger


async def test_zhihu_daily_fetcher():
    """测试知乎日报抓取器"""
    logger.info("开始测试知乎日报抓取器...")

    fetcher = ZhihuDailyFetcher()

    logger.info(f"开始抓取 {fetcher.source_name}")
    articles = await fetcher.fetch()

    logger.info(f"{fetcher.source_name} 抓取完成: {len(articles)} 条")

    if articles:
        logger.info("前5条知乎日报:")
        for i, article in enumerate(articles[:5], 1):
            logger.info(f"{i}. {article.title}")
            logger.info(f"   链接: {article.url}")
            logger.info(f"   优先级: {article.priority}")
            logger.info(f"   分类: {article.category}")
            logger.info("")
    else:
        logger.warning("未抓取到知乎日报数据")


if __name__ == "__main__":
    asyncio.run(test_zhihu_daily_fetcher())
