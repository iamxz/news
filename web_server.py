"""
Web 服务器入口（main.py 的别名）
"""
from main import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
