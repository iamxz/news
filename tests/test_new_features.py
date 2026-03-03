"""
测试新功能

测试 AFP 抓取器、交叉引用验证、定时任务
"""
import asyncio
from src.fetchers.afp import AFPFetcher
from src.fetchers.zaobao import ZaobaoFetcher
from src.validators.cross_reference import CrossReferenceValidator
from src.storage.models import NewsArticle
from datetime import datetime


async def test_afp_fetcher():
    """测试 AFP 抓取器"""
    print("=" * 60)
    print("测试 AFP 抓取器")
    print("=" * 60)
    
    fetcher = AFPFetcher()
    articles = await fetcher.fetch()
    
    print(f"✅ 抓取了 {len(articles)} 篇新闻")
    
    if articles:
        print("\n第一篇新闻:")
        print(f"  标题: {articles[0]['title']}")
        print(f"  链接: {articles[0]['url']}")
        print(f"  时间: {articles[0]['published_at']}")
    
    return articles


async def test_zaobao_fetcher():
    """测试联合早报抓取器"""
    print("\n" + "=" * 60)
    print("测试联合早报抓取器")
    print("=" * 60)
    
    fetcher = ZaobaoFetcher()
    articles = await fetcher.fetch()
    
    print(f"✅ 抓取了 {len(articles)} 篇新闻")
    
    if articles:
        print("\n第一篇新闻:")
        print(f"  标题: {articles[0]['title']}")
        print(f"  链接: {articles[0]['url']}")
        print(f"  时间: {articles[0]['published_at']}")
    
    return articles


def test_cross_reference_validator():
    """测试交叉引用验证器"""
    print("\n" + "=" * 60)
    print("测试交叉引用验证器")
    print("=" * 60)
    
    # 创建测试文章
    article = NewsArticle(
        id="test-001",
        title="Breaking News: Major Event Happens",
        content="This is a test article content.",
        source="TestSource",
        url="https://example.com/test",
        published_at=datetime.now(),
        category="test",
        priority=5
    )
    
    validator = CrossReferenceValidator()
    validated = validator.validate(article)
    
    print(f"✅ 交叉引用数: {validated.cross_references}")
    print(f"✅ 验证标签: {validated.verification_labels}")
    print(f"✅ 警告信息: {validated.warnings}")
    
    return validated


async def main():
    """主测试函数"""
    print("🧪 开始测试新功能...\n")
    
    # 测试 AFP
    try:
        await test_afp_fetcher()
    except Exception as e:
        print(f"❌ AFP 测试失败: {e}")
    
    # 测试联合早报
    try:
        await test_zaobao_fetcher()
    except Exception as e:
        print(f"❌ 联合早报测试失败: {e}")
    
    # 测试交叉引用
    try:
        test_cross_reference_validator()
    except Exception as e:
        print(f"❌ 交叉引用测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
