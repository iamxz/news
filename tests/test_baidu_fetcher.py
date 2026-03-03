import asyncio
from src.fetchers.baidu import BaiduFetcher

async def test_baidu_fetcher():
    print("测试百度热搜抓取器...")
    fetcher = BaiduFetcher()
    result = await fetcher.fetch()
    print(f"抓取结果: {len(result)} 条热搜")
    for item in result[:5]:
        print(f"  - {item.title}")

if __name__ == "__main__":
    asyncio.run(test_baidu_fetcher())