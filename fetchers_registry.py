"""
全球新闻聚合工具

新闻源注册中心
"""
from src.fetchers.reuters import ReutersFetcher
from src.fetchers.hackernews import HackerNewsFetcher
from src.fetchers.bloomberg import BloombergFetcher
from src.fetchers.ap_news import APNewsFetcher
from src.fetchers.bbc import BBCFetcher
from src.fetchers.guardian import GuardianFetcher
from src.fetchers.nytimes import NYTimesFetcher
from src.fetchers.aljazeera import AlJazeeraFetcher
from src.fetchers.techcrunch import TechCrunchFetcher
from src.fetchers.reddit import RedditFetcher
from src.fetchers.zaobao import ZaobaoFetcher
from src.fetchers.afp import AFPFetcher
from src.fetchers.washingtonpost import WashingtonPostFetcher
from src.fetchers.financialtimes import FinancialTimesFetcher
from src.fetchers.economist import EconomistFetcher
from src.fetchers.arstechnica import ArsTechnicaFetcher
from src.fetchers.theverge import TheVergeFetcher
from src.fetchers.googlenews import GoogleNewsFetcher
from src.fetchers.eightworld import EightWorldFetcher
from src.fetchers.nhkworld import NHKWorldFetcher
from src.fetchers.asahi import AsahiFetcher
from src.fetchers.mainichi import MainichiFetcher
from src.fetchers.japantimes import JapanTimesFetcher
from src.fetchers.shinmin import ShinMinFetcher
from src.fetchers.scmp import SCMPFetcher
from src.fetchers.initium import InitiumFetcher
from src.fetchers.toutiao import ToutiaoFetcher
from src.fetchers.baidu import BaiduFetcher
from src.fetchers.weibo import WeiboFetcher
from src.fetchers.ruanyifeng import RuanyifengFetcher
from src.fetchers.mittechreview import MITTechReviewFetcher


# 所有可用的新闻源抓取器
FETCHERS = {
    'reuters': ReutersFetcher,
    'hackernews': HackerNewsFetcher,
    'bloomberg': BloombergFetcher,
    'apnews': APNewsFetcher,
    'bbc': BBCFetcher,
    'guardian': GuardianFetcher,
    'nytimes': NYTimesFetcher,
    'aljazeera': AlJazeeraFetcher,
    'techcrunch': TechCrunchFetcher,
    'reddit': RedditFetcher,
    'zaobao': ZaobaoFetcher,
    'afp': AFPFetcher,
    'washingtonpost': WashingtonPostFetcher,
    'financialtimes': FinancialTimesFetcher,
    'economist': EconomistFetcher,
    'arstechnica': ArsTechnicaFetcher,
    'theverge': TheVergeFetcher,
    'googlenews': GoogleNewsFetcher,
    'eightworld': EightWorldFetcher,
    'nhkworld': NHKWorldFetcher,
    'asahi': AsahiFetcher,
    'mainichi': MainichiFetcher,
    'japantimes': JapanTimesFetcher,
    'shinmin': ShinMinFetcher,
    'scmp': SCMPFetcher,
    'initium': InitiumFetcher,
    'toutiao': ToutiaoFetcher,
    'baidu': BaiduFetcher,
    'weibo': WeiboFetcher,
    'ruanyifeng': RuanyifengFetcher,
    'mittechreview': MITTechReviewFetcher,
}
