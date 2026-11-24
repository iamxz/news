#!/usr/bin/env python3
"""
数据修复脚本

修正已有数据库中的错误数据：
1. 根据 source 设置正确的 language 字段
2. 根据原文语言填充 title_zh/content_zh 或 title_en/content_en
3. 标准化分类（热搜 -> 综合，头条 -> 综合 等）
"""
import sqlite3
import sys
from pathlib import Path

# 新闻源 -> 语言映射
SOURCE_LANGUAGE_MAP = {
    # 中文源
    '百度热搜': 'zh',
    '微博热搜': 'zh',
    '今日头条': 'zh',
    '抖音热榜': 'zh',
    '知乎日报': 'zh',
    'V2EX': 'zh',
    '少数派': 'zh',
    '36氪': 'zh',
    '阮一峰的网络日志': 'zh',
    'linuxdo': 'zh',
    # 英文源
    'BBC News': 'en',
    'Bloomberg': 'en',
    'Reuters': 'en',
    'Financial Times': 'en',
    'Google News': 'en',
    'MIT Technology Review': 'en',
    'SCMP': 'en',
    'TechCrunch': 'en',
    'The Guardian': 'en',
    'The New York Times': 'en',
    'The Verge': 'en',
    'Wall Street Journal': 'en',
    'Washington Post': 'en',
    'AFP': 'en',
}

# 分类标准化映射
CATEGORY_NORMALIZE = {
    '热搜': '综合',
    '头条': '综合',
    '日报': '综合',
    '市场': '财经',
    '美国新闻': '国际',
    '英国': '国际',
    '观点': '综合',
}


def detect_language_by_content(title: str, content: str) -> str:
    """通过内容检测语言"""
    text = (title or '') + (content or '')
    if not text:
        return 'en'
    cjk_count = sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff')
    if cjk_count > len(text) * 0.1:
        return 'zh'
    return 'en'


def normalize_category(category: str) -> str:
    """标准化分类"""
    if not category:
        return '综合'
    return CATEGORY_NORMALIZE.get(category, category)


def fix_database(db_path: str):
    """修复数据库中的语言和分类数据"""
    path = Path(db_path)
    if not path.exists():
        print(f"数据库不存在: {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 确保 language 列存在
    try:
        cursor.execute("SELECT language FROM articles LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE articles ADD COLUMN language TEXT DEFAULT 'en'")
        conn.commit()
        print("已添加 language 列")

    # 获取所有文章
    cursor.execute("SELECT id, title, title_zh, title_en, content, content_zh, content_en, source, category, language FROM articles")
    rows = cursor.fetchall()

    total = len(rows)
    fixed_lang = 0
    fixed_title = 0
    fixed_content = 0
    fixed_category = 0

    print(f"共 {total} 条新闻需要检查")

    for row in rows:
        article_id, title, title_zh, title_en, content, content_zh, content_en, source, category, language = row

        updates = {}

        # 1. 修正 language
        if not language:
            # 先根据 source 查找
            language = SOURCE_LANGUAGE_MAP.get(source)
            if not language:
                # 通过内容检测
                language = detect_language_by_content(title, content)
            updates['language'] = language
            fixed_lang += 1
        elif language not in ('zh', 'en', 'ja', 'ko', 'fr', 'de', 'es', 'ru'):
            # 非标准语言代码，重新检测
            new_lang = SOURCE_LANGUAGE_MAP.get(source)
            if not new_lang:
                new_lang = detect_language_by_content(title, content)
            if new_lang != language:
                updates['language'] = new_lang
                fixed_lang += 1
                language = new_lang

        # 2. 根据语言填充对应字段
        if language == 'zh':
            # 中文原文：填充 title_zh 和 content_zh
            if not title_zh and title:
                updates['title_zh'] = title
                fixed_title += 1
            if not content_zh and content:
                updates['content_zh'] = content
                fixed_content += 1
        else:
            # 英文原文：填充 title_en 和 content_en
            if not title_en and title:
                updates['title_en'] = title
                fixed_title += 1
            if not content_en and content:
                updates['content_en'] = content
                fixed_content += 1

        # 3. 标准化分类
        new_category = normalize_category(category)
        if new_category != category:
            updates['category'] = new_category
            fixed_category += 1

        # 执行更新
        if updates:
            set_clauses = ', '.join(f"{k} = ?" for k in updates)
            values = list(updates.values()) + [article_id]
            cursor.execute(f"UPDATE articles SET {set_clauses} WHERE id = ?", values)

    conn.commit()
    conn.close()

    print(f"\n修复完成:")
    print(f"  语言字段修正: {fixed_lang} 条")
    print(f"  标题字段填充: {fixed_title} 条")
    print(f"  内容字段填充: {fixed_content} 条")
    print(f"  分类标准化: {fixed_category} 条")
    print(f"  总计: {total} 条")


if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'data/news.db'
    fix_database(db_path)
