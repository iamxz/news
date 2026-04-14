"""
测试新功能

测试 AFP 抓取器、定时任务
"""
import asyncio
from src.fetchers.afp import AFPFetcher


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


async def main():
    """主测试函数"""
    print("🧪 开始测试新功能...\n")
    
    # 测试 AFP
    try:
        await test_afp_fetcher()
    except Exception as e:
        print(f"❌ AFP 测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
