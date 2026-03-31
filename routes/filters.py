"""
模板过滤器模块

注册 Jinja2 模板过滤器
"""
from datetime import datetime
from flask import Flask


def register_filters(app: Flask):
    """将所有模板过滤器注册到 Flask 应用"""

    @app.template_filter('format_datetime')
    def format_datetime_filter(value):
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
        if score >= 0.7:
            return 'blue'
        if score >= 0.5:
            return 'orange'
        return 'red'

    @app.template_filter('format_number')
    def format_number(num):
        """格式化数字为两位数字"""
        return f'{num:02d}'
