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
    """首页 - Tab 切换中英文，每个 Tab 下按媒体分块展示"""
    articles = db.get_articles()
    logger.info(f"首页获取到 {len(articles)} 条新闻")

    def _group_by_media(items):
        """将文章列表按媒体源分组并排序"""
        media_news = {}
        for article in items:
            media_news.setdefault(article.source, []).append(article)
        return dict(sorted(media_news.items()))

    # 按语言分为中文和英文两组，每组内部再按媒体分组
    cn_media = {}
    en_media = {}
    for article in articles:
        lang = getattr(article, 'language', 'en')
        if lang == 'zh':
            target = cn_media
        else:
            target = en_media
        target.setdefault(article.source, []).append(article)
    cn_media = dict(sorted(cn_media.items()))
    en_media = dict(sorted(en_media.items()))

    cn_count = sum(len(v) for v in cn_media.values())
    en_count = sum(len(v) for v in en_media.values())
    today_date = datetime.now().strftime('%Y-%m-%d')
    logger.info(f"中文新闻 {cn_count} 条，英文新闻 {en_count} 条")

    return render_template(
        'index.html',
        cn_media=cn_media,
        en_media=en_media,
        cn_count=cn_count,
        en_count=en_count,
        today_date=today_date,
    )


@frontend_bp.route('/list')
def list_page():
    """列表页 - 新闻列表"""
    page = request.args.get('page', 1, type=int)
    source = request.args.get('source', '')
    category = request.args.get('category', '')
    PER_PAGE = 50
    articles = db.get_articles(
        source=source, category=category,
        limit=PER_PAGE, offset=(page - 1) * PER_PAGE,
    )
    total = db.count_articles(
        source=source, category=category,
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
    )


@frontend_bp.route('/article/<article_id>')
def article_detail(article_id):
    """新闻详情页"""
    article = db.get_article_by_id(article_id)
    if not article:
        return "新闻不存在", 404
    return render_template('detail.html', article=article)
