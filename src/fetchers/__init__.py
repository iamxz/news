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
]
