"""新闻抓取器模块"""

from .reuters import ReutersFetcher
from .hackernews import HackerNewsFetcher
from .bloomberg import BloombergFetcher
from .ap_news import APNewsFetcher
from .bbc import BBCFetcher
from .guardian import GuardianFetcher
from .nytimes import NYTimesFetcher
from .aljazeera import AlJazeeraFetcher
from .techcrunch import TechCrunchFetcher
from .reddit import RedditFetcher
from .zaobao import ZaobaoFetcher
from .afp import AFPFetcher
from .washingtonpost import WashingtonPostFetcher
from .financialtimes import FinancialTimesFetcher
from .economist import EconomistFetcher
from .arstechnica import ArsTechnicaFetcher
from .theverge import TheVergeFetcher
from .googlenews import GoogleNewsFetcher
from .eightworld import EightWorldFetcher
from .nhkworld import NHKWorldFetcher
from .asahi import AsahiFetcher
from .mainichi import MainichiFetcher
from .japantimes import JapanTimesFetcher
from .shinmin import ShinMinFetcher
from .scmp import SCMPFetcher
from .initium import InitiumFetcher
from .toutiao import ToutiaoFetcher
from .baidu import BaiduFetcher
from .weibo import WeiboFetcher
from .ruanyifeng import RuanyifengFetcher
from .mittechreview import MITTechReviewFetcher

__all__ = [
    'ReutersFetcher',
    'HackerNewsFetcher',
    'BloombergFetcher',
    'APNewsFetcher',
    'BBCFetcher',
    'GuardianFetcher',
    'NYTimesFetcher',
    'AlJazeeraFetcher',
    'TechCrunchFetcher',
    'RedditFetcher',
    'ZaobaoFetcher',
    'AFPFetcher',
    'WashingtonPostFetcher',
    'FinancialTimesFetcher',
    'EconomistFetcher',
    'ArsTechnicaFetcher',
    'TheVergeFetcher',
    'GoogleNewsFetcher',
    'EightWorldFetcher',
    'NHKWorldFetcher',
    'AsahiFetcher',
    'MainichiFetcher',
    'JapanTimesFetcher',
    'ShinMinFetcher',
    'SCMPFetcher',
    'InitiumFetcher',
    'ToutiaoFetcher',
    'BaiduFetcher',
    'WeiboFetcher',
    'RuanyifengFetcher',
    'MITTechReviewFetcher',
]
