"""
API 接口路由

提供翻译、抓取、清理、调度器等 RESTful 接口
"""
import asyncio

from flask import Blueprint, request, jsonify

from src.storage.database import db
from src.storage.models import NewsArticle
from src.translators import translator_manager
from src.utils.logger import logger
from src.utils.translation_helper import translate_article as _do_translate
from src.utils import news_processor

api_bp = Blueprint('api', __name__, url_prefix='/api')


# ==================== 翻译接口 ====================

@api_bp.route('/translate/<article_id>', methods=['POST'])
def translate_article(article_id):
    """翻译单条新闻"""
    try:
        article = db.get_article_by_id(article_id)
        if not article:
            return jsonify({'success': False, 'error': '新闻不存在'}), 404

        # 已有完整翻译则直接返回
        if article.title_zh and article.title_en and article.content_zh and article.content_en:
            return jsonify({
                'success': True,
                'title_zh': article.title_zh, 'title_en': article.title_en,
                'content_zh': article.content_zh, 'content_en': article.content_en,
                'message': '已有翻译',
            })

        logger.info(f"开始翻译新闻: {article.title[:50]}")
        _do_translate(article, translator_manager)
        db.save_article(article)
        logger.info(f"翻译完成: {article.title[:50]}")

        return jsonify({
            'success': True,
            'title_zh': article.title_zh, 'title_en': article.title_en,
            'content_zh': article.content_zh, 'content_en': article.content_en,
            'message': '翻译成功',
        })
    except Exception as e:
        logger.error(f"翻译失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/translate-current-page', methods=['POST'])
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

                if article.title_zh and article.title_en and article.content_zh and article.content_en:
                    skipped_count += 1
                    continue

                _do_translate(article, translator_manager)
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
            'message': message,
        })
    except Exception as e:
        logger.error(f"批量翻译当前页失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== 管理 API ====================

@api_bp.route('/admin/fetch', methods=['POST'])
def admin_fetch():
    """执行抓取任务"""
    try:
        data = request.get_json()
        sources = data.get('sources', [])

        if not sources:
            return jsonify({'success': False, 'error': '请选择新闻源'})

        from src.fetchers.registry import FETCHERS
        total_articles = 0

        for source in sources:
            if source not in FETCHERS:
                continue

            try:
                fetcher = FETCHERS[source]()
                fetch_result = fetcher.fetch()

                # 兼容协程返回
                if asyncio.iscoroutine(fetch_result):
                    articles = asyncio.run(fetch_result)
                else:
                    articles = fetch_result

                # 使用 from_dict 统一转换
                article_objects = []
                for item in articles:
                    if isinstance(item, NewsArticle):
                        article_objects.append(item)
                        continue

                    article_dict = fetcher.normalize_article(item)
                    if fetcher.validate_article(article_dict):
                        article_objects.append(NewsArticle.from_dict(article_dict, fetcher))

                # 处理新闻（清洗和相似度判断）
                processed_articles = news_processor.process_articles(article_objects)
                count = db.save_articles(processed_articles)
                total_articles += count
                logger.info(f"{source} 抓取完成: {count} 条")
            except Exception as e:
                logger.error(f"{source} 抓取失败: {e}")
                continue

        return jsonify({
            'success': True,
            'message': f'成功抓取 {total_articles} 条新闻',
            'total': total_articles,
        })
    except Exception as e:
        logger.error(f"抓取失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/admin/translate-all', methods=['POST'])
def admin_translate_all():
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
                _do_translate(article, translator_manager)
                db.save_article(article)
                translated_count += 1
            except Exception as e:
                logger.error(f"翻译新闻失败 {article.id}: {e}")
                continue

        return jsonify({
            'success': True,
            'translated': translated_count,
            'total': len(articles),
            'message': f'成功翻译 {translated_count}/{len(articles)} 条新闻',
        })
    except Exception as e:
        logger.error(f"批量翻译失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/admin/clean', methods=['POST'])
def admin_clean():
    """清理新闻"""
    try:
        deleted = db.delete_all_articles()
        message = f'成功清理所有 {deleted} 条新闻'
        return jsonify({'success': True, 'deleted': deleted, 'message': message})
    except Exception as e:
        logger.error(f"清理失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 调度器 API ====================

@api_bp.route('/admin/scheduler/start', methods=['POST'])
def scheduler_start():
    """启动定时任务"""
    try:
        from src.scheduler.cron import start_scheduler
        start_scheduler()
        return jsonify({'success': True, 'message': '定时任务已启动'})
    except Exception as e:
        logger.error(f"启动定时任务失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/admin/scheduler/stop', methods=['POST'])
def scheduler_stop():
    """停止定时任务"""
    try:
        from src.scheduler.cron import stop_scheduler
        stop_scheduler()
        return jsonify({'success': True, 'message': '定时任务已停止'})
    except Exception as e:
        logger.error(f"停止定时任务失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/admin/scheduler/status')
def scheduler_status():
    """获取定时任务状态"""
    try:
        from src.scheduler.cron import get_scheduler_status
        status = get_scheduler_status()
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        logger.error(f"获取状态失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/admin/stats')
def admin_stats():
    """获取统计信息"""
    try:
        stats = db.get_statistics()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        logger.error(f"获取统计失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
