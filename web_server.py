"""
新闻展示 Web 应用

提供精美的新闻列表展示和翻页功能
"""
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
from src.storage.database import Database
from src.translators import translator_manager
from src.utils.config import get_settings
from src.utils.logger import logger

app = Flask(__name__)
db = Database()

# 每页显示的新闻数量
PER_PAGE = 20


@app.route('/')
def index():
    """首页 - 新闻列表"""
    page = request.args.get('page', 1, type=int)
    source = request.args.get('source', '')
    category = request.args.get('category', '')
    min_credibility = request.args.get('min_credibility', 0.0, type=float)
    days = request.args.get('days', 1, type=int)
    
    # 获取新闻列表
    articles = db.get_articles(
        source=source or None,
        category=category or None,
        min_credibility=min_credibility,
        days=days,
        limit=PER_PAGE,
        offset=(page - 1) * PER_PAGE
    )
    
    # 获取总数用于分页
    total = db.count_articles(
        source=source or None,
        category=category or None,
        min_credibility=min_credibility,
        days=days
    )
    
    total_pages = (total + PER_PAGE - 1) // PER_PAGE
    
    # 获取可用的新闻源和分类
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


@app.route('/api/translate/<article_id>', methods=['POST'])
def translate_article(article_id):
    """翻译新闻 API"""
    try:
        article = db.get_article_by_id(article_id)
        if not article:
            return jsonify({'success': False, 'error': '新闻不存在'}), 404
        
        # 如果已经翻译过，直接返回
        if article.title_zh and article.content_zh:
            return jsonify({
                'success': True,
                'title_zh': article.title_zh,
                'content_zh': article.content_zh,
                'message': '已有翻译'
            })
        
        # 翻译标题和内容
        logger.info(f"开始翻译新闻: {article.title[:50]}")
        
        title_zh = translator_manager.translate(article.title) if article.title else ''
        content_zh = translator_manager.translate(article.content) if article.content else ''
        
        if not title_zh and not content_zh:
            return jsonify({'success': False, 'error': '翻译服务不可用'}), 500
        
        # 更新数据库
        article.title_zh = title_zh or article.title_zh
        article.content_zh = content_zh or article.content_zh
        article.translated = True
        db.save_article(article)
        
        logger.info(f"翻译完成: {article.title[:50]}")
        
        return jsonify({
            'success': True,
            'title_zh': article.title_zh,
            'content_zh': article.content_zh,
            'message': '翻译成功'
        })
        
    except Exception as e:
        logger.error(f"翻译失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/translate-batch', methods=['POST'])
def translate_batch():
    """批量翻译未翻译的新闻"""
    try:
        data = request.get_json()
        limit = data.get('limit', 10)
        
        # 获取未翻译的新闻
        articles = db.get_untranslated_articles(limit=limit)
        
        if not articles:
            return jsonify({'success': True, 'translated': 0, 'message': '没有需要翻译的新闻'})
        
        translated_count = 0
        for article in articles:
            try:
                title_zh = translator_manager.translate(article.title) if article.title else ''
                content_zh = translator_manager.translate(article.content) if article.content else ''
                
                if title_zh or content_zh:
                    article.title_zh = title_zh or article.title_zh
                    article.content_zh = content_zh or article.content_zh
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
                
                # 如果已经翻译过，跳过
                if article.title_zh and article.content_zh:
                    skipped_count += 1
                    continue
                
                # 翻译
                title_zh = translator_manager.translate(article.title) if article.title else ''
                content_zh = translator_manager.translate(article.content) if article.content else ''
                
                if title_zh or content_zh:
                    article.title_zh = title_zh or article.title_zh
                    article.content_zh = content_zh or article.content_zh
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
    app.run(host='0.0.0.0', port=4000, debug=True)
