"""
管理后台页面路由

提供管理后台各页面
"""
from flask import Blueprint, render_template

from src.storage.database import db
from src.utils.config import get_settings

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('')
def dashboard():
    """管理后台首页"""
    stats = db.get_statistics()
    return render_template('admin/dashboard.html', stats=stats)


@admin_bp.route('/fetch')
def fetch():
    """抓取管理页面"""
    from src.fetchers.registry import FETCHERS

    categorized_fetchers = {'国际媒体': [], '中文媒体': []}

    for key, fetcher_class in FETCHERS.items():
        try:
            fetcher = fetcher_class()
            language = getattr(fetcher, 'language', 'en')
            target = '中文媒体' if language == 'zh' else '国际媒体'
            categorized_fetchers[target].append(key)
        except Exception:
            categorized_fetchers['国际媒体'].append(key)

    return render_template(
        'admin/fetch.html',
        categorized_fetchers=categorized_fetchers,
        total_count=len(FETCHERS),
    )


@admin_bp.route('/translate')
def translate():
    """翻译管理页面"""
    untranslated = db.get_untranslated_articles(limit=50)
    return render_template('admin/translate.html', articles=untranslated)


@admin_bp.route('/validate')
def validate():
    """验证管理页面"""
    unvalidated = db.get_unvalidated_articles(limit=50)
    return render_template('admin/validate.html', articles=unvalidated)


@admin_bp.route('/settings')
def settings():
    """系统设置页面"""
    return render_template('admin/settings.html', settings=get_settings())


@admin_bp.route('/scheduler')
def scheduler():
    """定时任务管理页面"""
    return render_template('admin/scheduler.html')
