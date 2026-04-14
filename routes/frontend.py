"""
前台页面路由

提供新闻首页、列表页、详情页
"""
from datetime import datetime

from flask import Blueprint, render_template, request

from src.storage.database import db
from src.utils.logger import logger

frontend_bp = Blueprint('frontend', __name__)

# 每页显示的新闻数量
@frontend_bp.route('/')
def index():
    """首页 - 按媒体分类展示当天新闻"""
    articles = db.get_articles()
    logger.info(f"首页获取到 {len(articles)} 条新闻")

    # 按媒体名称分组并排序
    media_news = {}
    for article in articles:
        media_news.setdefault(article.source, []).append(article)
    media_news = dict(sorted(media_news.items()))

    logger.info(f"媒体列表: {list(media_news.keys())}")
    today_date = datetime.now().strftime('%Y-%m-%d')

    return render_template('index.html', media_news=media_news, today_date=today_date)


@frontend_bp.route('/list')
def list_page():
    """列表页 - 新闻列表"""
    page = request.args.get('page', 1, type=int)
    source = request.args.get('source', '')
    category = request.args.get('category', '')
    min_credibility = request.args.get('min_credibility', 0.0, type=float)
    PER_PAGE = 50
    articles = db.get_articles(
        source=source, category=category,
        min_credibility=min_credibility,
        limit=PER_PAGE, offset=(page - 1) * PER_PAGE,
    )
    total = db.count_articles(
        source=source, category=category,
        min_credibility=min_credibility,
    )
    total_pages = (total + PER_PAGE - 1) // PER_PAGE

    return render_template(
        'list.html',
        articles=articles,
        page=page,
        total_pages=total_pages,
        total=total,
        sources=db.get_all_sources(),
        categories=db.get_all_categories(),
        current_source=source,
        current_category=category,
        min_credibility=min_credibility,
    )


@frontend_bp.route('/article/<article_id>')
def article_detail(article_id):
    """新闻详情页"""
    article = db.get_article_by_id(article_id)
    if not article:
        return "新闻不存在", 404
    return render_template('detail.html', article=article)
