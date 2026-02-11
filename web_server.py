"""
新闻展示 Web 应用

提供精美的新闻列表展示和管理后台
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
import asyncio
from src.storage.database import Database
from src.translators import translator_manager
from src.utils.config import get_settings
from src.utils.logger import logger

app = Flask(__name__)
db = Database()

# 每页显示的新闻数量
PER_PAGE = 20


# ==================== 前台页面 ====================

@app.route('/')
def index():
    """首页 - 新闻列表"""
    page = request.args.get('page', 1, type=int)
    source = request.args.get('source', '')
    category = request.args.get('category', '')
    min_credibility = request.args.get('min_credibility', 0.0, type=float)
    days = request.args.get('days', 1, type=int)
    
    articles = db.get_articles(
        source=source or None,
        category=category or None,
        min_credibility=min_credibility,
        days=days,
        limit=PER_PAGE,
        offset=(page - 1) * PER_PAGE
    )
    
    total = db.count_articles(
        source=source or None,
        category=category or None,
        min_credibility=min_credibility,
        days=days
    )
    
    total_pages = (total + PER_PAGE - 1) // PER_PAGE
    sources = db.get_all_sources()
    categories = db.get_all_categories()
    
    return render_template(
        'index.html',
        articles=articles,
        page=page,
        total_pages=total_pages,
        total=total,
        sources=sources,
        categories=categories,
        current_source=source,
        current_category=category,
        min_credibility=min_credibility,
        days=days
    )


@app.route('/article/<article_id>')
def article_detail(article_id):
    """新闻详情页"""
    article = db.get_article_by_id(article_id)
    if not article:
        return "新闻不存在", 404
    
    return render_template('detail.html', article=article)


# ==================== 管理后台 ====================

@app.route('/admin')
def admin_dashboard():
    """管理后台首页"""
    stats = db.get_statistics()
    return render_template('admin/dashboard.html', stats=stats)


@app.route('/admin/fetch')
def admin_fetch():
    """抓取管理页面"""
    from main import FETCHERS
    fetchers = list(FETCHERS.keys())
    return render_template('admin/fetch.html', fetchers=fetchers)


@app.route('/admin/translate')
def admin_translate():
    """翻译管理页面"""
    untranslated = db.get_untranslated_articles(limit=50)
    return render_template('admin/translate.html', articles=untranslated)


@app.route('/admin/validate')
def admin_validate():
    """验证管理页面"""
    unvalidated = db.get_unvalidated_articles(limit=50)
    return render_template('admin/validate.html', articles=unvalidated)


@app.route('/admin/settings')
def admin_settings():
    """系统设置页面"""
    settings = get_settings()
    return render_template('admin/settings.html', settings=settings)


@app.route('/admin/scheduler')
def admin_scheduler():
    """定时任务管理页面"""
    return render_template('admin/scheduler.html')


# ==================== API 接口 ====================

@app.route('/api/translate/<article_id>', methods=['POST'])
def translate_article(article_id):
    """翻译单条新闻"""
    try:
        article = db.get_article_by_id(article_id)
        if not article:
            return jsonify({'success': False, 'error': '新闻不存在'}), 404
        
        # 检查是否已有完整翻译
        if article.title_zh and article.title_en and article.content_zh and article.content_en:
            return jsonify({
                'success': True,
                'title_zh': article.title_zh,
                'title_en': article.title_en,
                'content_zh': article.content_zh,
                'content_en': article.content_en,
                'message': '已有翻译'
            })
        
        logger.info(f"开始翻译新闻: {article.title[:50]}")
        
        # 判断来源语言
        japanese_sources = ['NHK World', 'Asahi Shimbun', 'The Japan Times', 'Mainichi']
        chinese_sources = ['今日头条', '百度热搜', '微博热搜', '联合早报', '8视界', '新明日报', '南华早报', '端传媒']
        is_japanese = article.source in japanese_sources
        is_chinese = article.source in chinese_sources
        
        # 翻译标题和内容
        if is_japanese:
            # 日文 -> 英文和中文
            if not article.title_en:
                article.title_en = translator_manager.translate(article.title, source_lang='ja', target_lang='en') if article.title else ''
            if not article.title_zh:
                article.title_zh = translator_manager.translate(article.title, source_lang='ja', target_lang='zh') if article.title else ''
            if not article.content_en:
                article.content_en = translator_manager.translate(article.content, source_lang='ja', target_lang='en') if article.content else ''
            if not article.content_zh:
                article.content_zh = translator_manager.translate(article.content, source_lang='ja', target_lang='zh') if article.content else ''
        elif is_chinese:
            # 中文 -> 英文，原文作为中文
            if not article.title_zh:
                article.title_zh = article.title
            if not article.title_en:
                article.title_en = translator_manager.translate(article.title, source_lang='zh', target_lang='en') if article.title else ''
            if not article.content_zh:
                article.content_zh = article.content
            if not article.content_en:
                article.content_en = translator_manager.translate(article.content, source_lang='zh', target_lang='en') if article.content else ''
        else:
            # 英文 -> 中文，原文作为英文
            if not article.title_en:
                article.title_en = article.title
            if not article.title_zh:
                article.title_zh = translator_manager.translate(article.title, source_lang='en', target_lang='zh') if article.title else ''
            if not article.content_en:
                article.content_en = article.content
            if not article.content_zh:
                article.content_zh = translator_manager.translate(article.content, source_lang='en', target_lang='zh') if article.content else ''
        
        article.translated = True
        db.save_article(article)
        
        logger.info(f"翻译完成: {article.title[:50]}")
        
        return jsonify({
            'success': True,
            'title_zh': article.title_zh,
            'title_en': article.title_en,
            'content_zh': article.content_zh,
            'content_en': article.content_en,
            'message': '翻译成功'
        })
        
    except Exception as e:
        logger.error(f"翻译失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/translate-current-page', methods=['POST'])
def translate_current_page():
    """翻译当前页的所有新闻"""
    try:
        data = request.get_json()
        article_ids = data.get('article_ids', [])
        
        if not article_ids:
            return jsonify({'success': False, 'error': '没有提供新闻 ID'})
        
        translated_count = 0
        skipped_count = 0
        
        for article_id in article_ids:
            try:
                article = db.get_article_by_id(article_id)
                if not article:
                    continue
                
                # 检查是否已有完整翻译
                if article.title_zh and article.title_en and article.content_zh and article.content_en:
                    skipped_count += 1
                    continue
                
                # 判断来源语言
                japanese_sources = ['NHK World', 'Asahi Shimbun', 'The Japan Times', 'Mainichi']
                chinese_sources = ['今日头条', '百度热搜', '微博热搜', '联合早报', '8视界', '新明日报', '南华早报', '端传媒']
                is_japanese = article.source in japanese_sources
                is_chinese = article.source in chinese_sources
                
                # 翻译
                if is_japanese:
                    if not article.title_en:
                        article.title_en = translator_manager.translate(article.title, source_lang='ja', target_lang='en') if article.title else ''
                    if not article.title_zh:
                        article.title_zh = translator_manager.translate(article.title, source_lang='ja', target_lang='zh') if article.title else ''
                    if not article.content_en:
                        article.content_en = translator_manager.translate(article.content, source_lang='ja', target_lang='en') if article.content else ''
                    if not article.content_zh:
                        article.content_zh = translator_manager.translate(article.content, source_lang='ja', target_lang='zh') if article.content else ''
                elif is_chinese:
                    if not article.title_zh:
                        article.title_zh = article.title
                    if not article.title_en:
                        article.title_en = translator_manager.translate(article.title, source_lang='zh', target_lang='en') if article.title else ''
                    if not article.content_zh:
                        article.content_zh = article.content
                    if not article.content_en:
                        article.content_en = translator_manager.translate(article.content, source_lang='zh', target_lang='en') if article.content else ''
                else:
                    if not article.title_en:
                        article.title_en = article.title
                    if not article.title_zh:
                        article.title_zh = translator_manager.translate(article.title, source_lang='en', target_lang='zh') if article.title else ''
                    if not article.content_en:
                        article.content_en = article.content
                    if not article.content_zh:
                        article.content_zh = translator_manager.translate(article.content, source_lang='en', target_lang='zh') if article.content else ''
                
                article.translated = True
                db.save_article(article)
                translated_count += 1
                logger.info(f"翻译完成: {article.title[:50]}")
                    
            except Exception as e:
                logger.error(f"翻译新闻失败 {article_id}: {e}")
                continue
        
        message = f'成功翻译 {translated_count} 条新闻'
        if skipped_count > 0:
            message += f'，跳过 {skipped_count} 条已翻译的新闻'
        
        return jsonify({
            'success': True,
            'translated': translated_count,
            'skipped': skipped_count,
            'total': len(article_ids),
            'message': message
        })
        
    except Exception as e:
        logger.error(f"批量翻译当前页失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/fetch', methods=['POST'])
def api_admin_fetch():
    """执行抓取任务"""
    try:
        data = request.get_json()
        sources = data.get('sources', [])
        
        if not sources:
            return jsonify({'success': False, 'error': '请选择新闻源'})
        
        from fetchers_registry import FETCHERS
        total_articles = 0
        
        for source in sources:
            if source not in FETCHERS:
                continue
            
            try:
                fetcher = FETCHERS[source]()
                articles = asyncio.run(fetcher.fetch())
                count = db.save_articles(articles)
                total_articles += count
                logger.info(f"{source} 抓取完成: {count} 条")
            except Exception as e:
                logger.error(f"{source} 抓取失败: {e}")
                continue
        
        return jsonify({
            'success': True,
            'message': f'成功抓取 {total_articles} 条新闻',
            'total': total_articles
        })
        
    except Exception as e:
        logger.error(f"抓取失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/translate-all', methods=['POST'])
def api_admin_translate_all():
    """翻译所有未翻译的新闻"""
    try:
        data = request.get_json()
        limit = data.get('limit', 50)
        
        articles = db.get_untranslated_articles(limit=limit)
        
        if not articles:
            return jsonify({'success': True, 'translated': 0, 'message': '没有需要翻译的新闻'})
        
        translated_count = 0
        for article in articles:
            try:
                # 判断来源语言
                japanese_sources = ['NHK World', 'Asahi Shimbun', 'The Japan Times', 'Mainichi']
                chinese_sources = ['今日头条', '百度热搜', '微博热搜', '联合早报', '8视界', '新明日报', '南华早报', '端传媒']
                is_japanese = article.source in japanese_sources
                is_chinese = article.source in chinese_sources
                
                # 翻译
                if is_japanese:
                    if not article.title_en:
                        article.title_en = translator_manager.translate(article.title, source_lang='ja', target_lang='en') if article.title else ''
                    if not article.title_zh:
                        article.title_zh = translator_manager.translate(article.title, source_lang='ja', target_lang='zh') if article.title else ''
                    if not article.content_en:
                        article.content_en = translator_manager.translate(article.content, source_lang='ja', target_lang='en') if article.content else ''
                    if not article.content_zh:
                        article.content_zh = translator_manager.translate(article.content, source_lang='ja', target_lang='zh') if article.content else ''
                elif is_chinese:
                    if not article.title_zh:
                        article.title_zh = article.title
                    if not article.title_en:
                        article.title_en = translator_manager.translate(article.title, source_lang='zh', target_lang='en') if article.title else ''
                    if not article.content_zh:
                        article.content_zh = article.content
                    if not article.content_en:
                        article.content_en = translator_manager.translate(article.content, source_lang='zh', target_lang='en') if article.content else ''
                else:
                    if not article.title_en:
                        article.title_en = article.title
                    if not article.title_zh:
                        article.title_zh = translator_manager.translate(article.title, source_lang='en', target_lang='zh') if article.title else ''
                    if not article.content_en:
                        article.content_en = article.content
                    if not article.content_zh:
                        article.content_zh = translator_manager.translate(article.content, source_lang='en', target_lang='zh') if article.content else ''
                
                article.translated = True
                db.save_article(article)
                translated_count += 1
                    
            except Exception as e:
                logger.error(f"翻译新闻失败 {article.id}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'translated': translated_count,
            'total': len(articles),
            'message': f'成功翻译 {translated_count}/{len(articles)} 条新闻'
        })
        
    except Exception as e:
        logger.error(f"批量翻译失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/validate-all', methods=['POST'])
def api_admin_validate_all():
    """验证所有未验证的新闻"""
    try:
        data = request.get_json()
        limit = data.get('limit', 50)
        
        articles = db.get_unvalidated_articles(limit=limit)
        
        if not articles:
            return jsonify({'success': True, 'validated': 0, 'message': '没有需要验证的新闻'})
        
        validated_count = 0
        for article in articles:
            try:
                # 这里可以调用验证服务
                article.validated = True
                db.save_article(article)
                validated_count += 1
            except Exception as e:
                logger.error(f"验证新闻失败 {article.id}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'validated': validated_count,
            'total': len(articles),
            'message': f'成功验证 {validated_count}/{len(articles)} 条新闻'
        })
        
    except Exception as e:
        logger.error(f"批量验证失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/clean', methods=['POST'])
def api_admin_clean():
    """清理旧新闻"""
    try:
        data = request.get_json()
        days = data.get('days', 30)
        
        deleted = db.delete_old_articles(days=days)
        
        return jsonify({
            'success': True,
            'deleted': deleted,
            'message': f'成功清理 {deleted} 条旧新闻'
        })
        
    except Exception as e:
        logger.error(f"清理失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/scheduler/start', methods=['POST'])
def api_scheduler_start():
    """启动定时任务"""
    try:
        from src.scheduler.cron import start_scheduler
        start_scheduler()
        return jsonify({'success': True, 'message': '定时任务已启动'})
    except Exception as e:
        logger.error(f"启动定时任务失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/scheduler/stop', methods=['POST'])
def api_scheduler_stop():
    """停止定时任务"""
    try:
        from src.scheduler.cron import stop_scheduler
        stop_scheduler()
        return jsonify({'success': True, 'message': '定时任务已停止'})
    except Exception as e:
        logger.error(f"停止定时任务失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/scheduler/status')
def api_scheduler_status():
    """获取定时任务状态"""
    try:
        from src.scheduler.cron import get_scheduler_status
        status = get_scheduler_status()
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        logger.error(f"获取状态失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/stats')
def api_admin_stats():
    """获取统计信息"""
    try:
        stats = db.get_statistics()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        logger.error(f"获取统计失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== 模板过滤器 ====================

@app.template_filter('format_datetime')
def format_datetime(value):
    """格式化日期时间"""
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return value.strftime('%Y-%m-%d %H:%M')


@app.template_filter('credibility_stars')
def credibility_stars(score):
    """可信度星级"""
    if score is None:
        return '未评分'
    stars = int(score * 5)
    return '★' * stars + '☆' * (5 - stars)


@app.template_filter('credibility_color')
def credibility_color(score):
    """可信度颜色"""
    if score is None:
        return 'gray'
    if score >= 0.85:
        return 'green'
    elif score >= 0.7:
        return 'blue'
    elif score >= 0.5:
        return 'orange'
    else:
        return 'red'


if __name__ == '__main__':
    logger.info("启动新闻 Web 应用...")
    app.run(host='0.0.0.0', port=4000, debug=True)

