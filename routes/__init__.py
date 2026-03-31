"""
路由模块

提供 Blueprint 注册功能
"""
from flask import Flask

from routes.filters import register_filters
from routes.frontend import frontend_bp
from routes.admin import admin_bp
from routes.api import api_bp


def register_blueprints(app: Flask):
    """将所有 Blueprint 和模板过滤器注册到 Flask 应用"""
    register_filters(app)
    app.register_blueprint(frontend_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
