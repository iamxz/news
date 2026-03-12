"""
测试新闻抓取器
"""
from fetchers_registry import FETCHERS

def test_fetchers():
    """测试所有抓取器"""
    # 测试BBC
    if 'bbc' in FETCHERS:
        print("测试BBC抓取器...")
        bbc_fetcher = FETCHERS['bbc']()
        bbc_news = bbc_fetcher.fetch()
        print(f"BBC 抓取到 {len(bbc_news)} 条新闻")
    
    # 测试Reuters
    if 'reuters' in FETCHERS:
        print("\n测试Reuters抓取器...")
        reuters_fetcher = FETCHERS['reuters']()
        reuters_news = reuters_fetcher.fetch()
        print(f"Reuters 抓取到 {len(reuters_news)} 条新闻")
    
    # 测试纽约时报
    if 'nytimes' in FETCHERS:
        print("\n测试纽约时报抓取器...")
        nytimes_fetcher = FETCHERS['nytimes']()
        nytimes_news = nytimes_fetcher.fetch()
        print(f"纽约时报 抓取到 {len(nytimes_news)} 条新闻")
    
    # 测试36氪
    if '36kr' in FETCHERS:
        print("\n测试36氪抓取器...")
        kr36_fetcher = FETCHERS['36kr']()
        kr36_news = kr36_fetcher.fetch()
        print(f"36氪 抓取到 {len(kr36_news)} 条新闻")
    
    # 测试少数派
    if 'sspai' in FETCHERS:
        print("\n测试少数派抓取器...")
        sspai_fetcher = FETCHERS['sspai']()
        sspai_news = sspai_fetcher.fetch()
        print(f"少数派 抓取到 {len(sspai_news)} 条新闻")

if __name__ == "__main__":
    test_fetchers()