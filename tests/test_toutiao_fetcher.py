import asyncio
from src.fetchers.toutiao import ToutiaoFetcher

async def test_toutiao_fetcher():
    print("测试今日头条热搜抓取器...")
    fetcher = ToutiaoFetcher()
    result = await fetcher.fetch()
    print(f"抓取结果: {len(result)} 条热搜")
    for item in result[:5]:
        print(f"  - {item.title}")

if __name__ == "__main__":
    asyncio.run(test_toutiao_fetcher())