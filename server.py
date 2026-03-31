"""
新闻展示 Web 应用

提供精美的新闻列表展示和管理后台
"""
from flask import Flask

from routes import register_blueprints
from src.utils.logger import logger


def create_app() -> Flask:
    """应用工厂：创建并配置 Flask 实例"""
    app = Flask(__name__)
    register_blueprints(app)
    return app


app = create_app()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='新闻 Web 应用')
    parser.add_argument('--port', type=int, default=4000, help='服务器端口')
    args = parser.parse_args()

    logger.info(f"启动新闻 Web 应用... 端口: {args.port}")
    app.run(host='0.0.0.0', port=args.port, debug=True)
