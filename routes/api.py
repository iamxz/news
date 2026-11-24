"""
API 接口路由

提供翻译、抓取、清理、调度器等 RESTful 接口
"""
import asyncio
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

from flask import Blueprint, request, jsonify

from src.storage.database import db
from src.storage.models import NewsArticle
from src.translators import translator_manager
from src.translators.base import BaseTranslator
from src.utils.logger import logger
from src.utils.translation_helper import translate_article as _do_translate
from src.utils import news_processor

api_bp = Blueprint('api', __name__, url_prefix='/api')


def _get_available_translators() -> List[BaseTranslator]:
    """获取所有当前可用的翻译器列表"""
    return [t for t in translator_manager.translators if t.is_available()]


def _translate_with_round_robin(
    article: NewsArticle,
    translators: List[BaseTranslator],
    translator_idx: int,
) -> tuple[bool, str, int]:
    """
    使用轮换翻译器翻译单篇文章，防止对同一平台频繁请求。

    Args:
        article: 待翻译文章
        translators: 可用翻译器列表
        translator_idx: 起始翻译器索引（轮换起点）

    Returns:
        (是否成功, 翻译器名称, 下一个翻译器索引)
    """
    if not translators:
        return False, "无可用翻译器", translator_idx

    source_lang = getattr(article, 'language', 'en')

    # 最多尝试所有翻译器
    n = len(translators)
    for attempt in range(n):
        idx = (translator_idx + attempt) % n
        translator = translators[idx]
        try:
            logger.info(f"[轮换] 使用 {translator.name} 翻译: {article.title[:50]}")

            if source_lang == 'zh':
                if not article.title_en:
                    article.title_en = translator.translate(article.title, 'zh', 'en') or ''
                if not article.content_en:
                    article.content_en = translator.translate(article.content, 'zh', 'en') or ''
                if not article.title_zh:
                    article.title_zh = article.title
                if not article.content_zh:
                    article.content_zh = article.content
            else:
                if not article.title_zh:
                    article.title_zh = translator.translate(article.title, 'en', 'zh') or ''
                if not article.content_zh:
                    article.content_zh = translator.translate(article.content, 'en', 'zh') or ''
                if not article.title_en:
                    article.title_en = article.title
                if not article.content_en:
                    article.content_en = article.content

            article.translated = True
            next_idx = (idx + 1) % n  # 下次从下一个翻译器开始
            return True, translator.name, next_idx
        except Exception as e:
            logger.warning(f"[轮换] {translator.name} 翻译失败: {e}，尝试下一个")
            continue

    return False, "全部失败", (translator_idx + 1) % n


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
    """
    一键并发翻译所有英文未翻译新闻。

    使用多翻译器轮换 + 线程池并发，防止单一平台被频繁请求。
    每篇文章随机选择起始翻译器，并在翻译器间轮换。

    请求体（JSON）：
        - limit: 翻译数量上限（默认 50）
    """
    try:
        data = request.get_json() or {}
        limit = data.get('limit', 50)

        # 只获取英文未翻译新闻
        articles = db.get_untranslated_en_articles(limit=limit)
        if not articles:
            return jsonify({
                'success': True,
                'translated': 0,
                'total': 0,
                'message': '没有需要翻译的英文新闻',
            })

        # 获取可用翻译器
        translators = _get_available_translators()
        if not translators:
            return jsonify({
                'success': False,
                'error': '没有可用的翻译器，请检查翻译服务配置',
            }), 500

        logger.info(
            f"开始并发翻译: {len(articles)} 篇文章, "
            f"{len(translators)} 个翻译器 "
            f"({', '.join(t.name for t in translators)})"
        )

        translated_count = 0
        failed_count = 0
        translator_usage: dict[str, int] = {}

        # 使用线程池并发翻译，并发数为翻译器数量（每个翻译器同时处理一篇）
        max_workers = min(len(translators), len(articles))
        # 每篇文章随机选择起始翻译器索引
        start_indices = [random.randint(0, len(translators) - 1) for _ in articles]

        def _translate_one(task_idx: int) -> tuple[bool, str, int]:
            """翻译单篇文章的包装函数，加入随机延迟防止并发轰炸"""
            article = articles[task_idx]
            idx = start_indices[task_idx]
            # 随机延迟 0.2~1.0 秒，错开请求
            time.sleep(random.uniform(0.2, 1.0))
            success, translator_name, next_idx = _translate_with_round_robin(
                article, translators, idx
            )
            if success:
                db.save_article(article)
            return task_idx, success, translator_name, next_idx

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(_translate_one, i): i
                for i in range(len(articles))
            }
            for future in as_completed(futures):
                try:
                    task_idx, success, translator_name, _ = future.result()
                    if success:
                        translated_count += 1
                        translator_usage[translator_name] = (
                            translator_usage.get(translator_name, 0) + 1
                        )
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"并发翻译任务异常: {e}")
                    failed_count += 1

        usage_str = ', '.join(
            f"{name}: {count}" for name, count in translator_usage.items()
        )
        message = f'成功翻译 {translated_count}/{len(articles)} 条新闻'
        if failed_count > 0:
            message += f'，失败 {failed_count} 条'
        if usage_str:
            message += f'（翻译器使用: {usage_str}）'

        logger.info(f"并发翻译完成: {message}")

        return jsonify({
            'success': True,
            'translated': translated_count,
            'failed': failed_count,
            'total': len(articles),
            'translator_usage': translator_usage,
            'message': message,
        })
    except Exception as e:
        logger.error(f"批量翻译失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/admin/clean', methods=['POST'])
def admin_clean():
    """清理新闻

    请求体（JSON）：
        - mode: "all" | "before_date"  （默认 all）
        - before_date: "YYYY-MM-DD"    （mode=before_date 时必填）
    """
    try:
        data = request.get_json() or {}
        mode = data.get('mode', 'all')

        if mode == 'before_date':
            before_date_str = data.get('before_date', '')
            if not before_date_str:
                return jsonify({'success': False, 'error': '请提供 before_date 参数'}), 400

            from datetime import datetime
            try:
                before_date = datetime.strptime(before_date_str, '%Y-%m-%d')
            except ValueError:
                return jsonify({'success': False, 'error': '日期格式无效，请使用 YYYY-MM-DD'}), 400

            deleted = db.delete_articles_before_date(before_date)
            message = f'成功清理 {before_date_str} 之前的 {deleted} 条新闻'
        else:
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
