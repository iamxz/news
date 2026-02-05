
import json
import webbrowser
import os
from datetime import datetime
from typing import List
from pathlib import Path

from src.storage.models import NewsArticle
from src.utils.logger import logger

def generate_and_open_report(articles: List[NewsArticle], output_file: str = "news_report.html"):
    """
    生成新闻 HTML 报告并在浏览器中打开
    
    Args:
        articles: 新闻列表
        output_file: 输出文件名
    """
    html_content = _generate_html(articles)
    
    # 获取绝对路径
    file_path = Path(output_file).resolve()
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logger.info(f"生成新闻报告: {file_path}")
        print(f"正在浏览器中打开: {file_path}")
        
        webbrowser.open(f"file://{file_path}")
        
    except Exception as e:
        logger.error(f"生成报告失败: {e}", exc_info=True)
        print(f"生成报告失败: {e}")

def _generate_html(articles: List[NewsArticle]) -> str:
    """生成 HTML 内容"""
    
    # 准备数据
    articles_data = []
    for article in articles:
        articles_data.append({
            "id": article.id,
            "title": article.title,
            "title_zh": article.title_zh,
            "source": article.source,
            "category": article.category,
            "published_at": article.published_at.strftime("%Y-%m-%d %H:%M"),
            "credibility_score": article.credibility_score,
            "content": article.content,
            "content_zh": article.content_zh,
            "url": article.url,
            "verification_labels": article.verification_labels,
            "warnings": article.warnings
        })
    
    json_data = json.dumps(articles_data, ensure_ascii=False)
    
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>新闻聚合报告</title>
    <style>
        :root {{
            --bg-color: #f8f9fa;
            --card-bg: #ffffff;
            --text-color: #333333;
            --secondary-text: #666666;
            --border-color: #e9ecef;
            --primary-color: #007bff;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --danger-color: #dc3545;
        }}
        
        @media (prefers-color-scheme: dark) {{
            :root {{
                --bg-color: #121212;
                --card-bg: #1e1e1e;
                --text-color: #e0e0e0;
                --secondary-text: #aaaaaa;
                --border-color: #333333;
                --primary-color: #4dabf7;
            }}
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }}

        h1 {{ margin: 0; }}

        .search-box {{
            padding: 10px;
            border: 1px solid var(--border-color);
            border-radius: 5px;
            width: 300px;
            background-color: var(--card-bg);
            color: var(--text-color);
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }}

        .card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}

        .card-meta {{
            display: flex;
            justify-content: space-between;
            font-size: 0.85em;
            color: var(--secondary-text);
            margin-bottom: 10px;
        }}

        .card-title {{
            font-size: 1.1em;
            font-weight: bold;
            margin-bottom: 10px;
            color: var(--primary-color);
        }}

        .card-title-zh {{
            font-size: 1em;
            margin-bottom: 10px;
        }}

        .credibility {{
            display: inline-block;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        
        .cred-high {{ background-color: rgba(40, 167, 69, 0.2); color: var(--success-color); }}
        .cred-med {{ background-color: rgba(255, 193, 7, 0.2); color: var(--warning-color); }}
        .cred-low {{ background-color: rgba(220, 53, 69, 0.2); color: var(--danger-color); }}

        /* Modal */
        .modal-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0, 0, 0, 0.7);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }}

        .modal {{
            background-color: var(--card-bg);
            width: 90%;
            max-width: 800px;
            max-height: 90vh;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        }}

        .modal-header {{
            padding: 20px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}

        .close-btn {{
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: var(--secondary-text);
        }}

        .modal-body {{
            padding: 20px;
            overflow-y: auto;
        }}

        .modal-footer {{
            padding: 20px;
            border-top: 1px solid var(--border-color);
            text-align: right;
        }}

        .tag {{
            display: inline-block;
            padding: 2px 8px;
            background-color: var(--border-color);
            border-radius: 12px;
            font-size: 0.8em;
            margin-right: 5px;
            margin-bottom: 5px;
        }}

        .content-box {{
            background-color: rgba(0,0,0,0.03);
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
            white-space: pre-wrap;
        }}

        .btn {{
            display: inline-block;
            padding: 8px 16px;
            background-color: var(--primary-color);
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        
        .hidden {{ display: none; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>全球新闻聚合 <span style="font-size: 0.5em; color: var(--secondary-text);">generated at {datetime.now().strftime('%Y-%m-%d %H:%M')}</span></h1>
            <input type="text" id="searchInput" class="search-box" placeholder="搜索标题..." onkeyup="filterArticles()">
        </header>

        <div id="articlesGrid" class="grid">
            <!-- Articles will be injected here -->
        </div>
    </div>

    <!-- Modal -->
    <div id="detailModal" class="modal-overlay" onclick="closeModal(event)">
        <div class="modal" onclick="event.stopPropagation()">
            <div class="modal-header">
                <div id="modalTitle"></div>
                <button class="close-btn" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body" id="modalBody">
                <!-- Content -->
            </div>
            <div class="modal-footer">
                <a id="sourceLink" href="#" target="_blank" class="btn">查看原文 ↗</a>
            </div>
        </div>
    </div>

    <script>
        const articles = {json_data};

        function renderArticles(list) {{
            const grid = document.getElementById('articlesGrid');
            grid.innerHTML = '';

            if (list.length === 0) {{
                grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--secondary-text);">没有找到匹配的新闻</p>';
                return;
            }}

            list.forEach(article => {{
                const card = document.createElement('div');
                card.className = 'card';
                card.onclick = () => showDetail(article.id);

                const credClass = article.credibility_score >= 0.8 ? 'cred-high' : 
                                 (article.credibility_score >= 0.5 ? 'cred-med' : 'cred-low');
                
                const titleZh = article.title_zh ? `<div class="card-title-zh">${{article.title_zh}}</div>` : '';

                card.innerHTML = `
                    <div class="card-meta">
                        <span>${{article.source}} · ${{article.category}}</span>
                        <span>${{article.published_at.split(' ')[0]}}</span>
                    </div>
                    <div class="card-title">${{article.title}}</div>
                    ${{titleZh}}
                    <div style="margin-top: 10px;">
                        <span class="credibility ${{credClass}}">可信度: ${{article.credibility_score.toFixed(2)}}</span>
                    </div>
                `;
                grid.appendChild(card);
            }});
        }}

        function filterArticles() {{
            const query = document.getElementById('searchInput').value.toLowerCase();
            const filtered = articles.filter(a => 
                a.title.toLowerCase().includes(query) || 
                (a.title_zh && a.title_zh.toLowerCase().includes(query)) ||
                a.source.toLowerCase().includes(query)
            );
            renderArticles(filtered);
        }}

        function showDetail(id) {{
            const article = articles.find(a => a.id === id);
            if (!article) return;

            const titleDiv = document.getElementById('modalTitle');
            titleDiv.innerHTML = `
                <h2 style="margin: 0; color: var(--primary-color);">${{article.title}}</h2>
                ${{article.title_zh ? `<h3 style="margin: 5px 0 0 0; font-weight: normal;">${{article.title_zh}}</h3>` : ''}}
            `;

            const bodyDiv = document.getElementById('modalBody');
            
            let contentHtml = '';
            
            // Meta info
            contentHtml += `
                <div style="margin-bottom: 20px; color: var(--secondary-text); font-size: 0.9em;">
                    <span style="margin-right: 15px;">📅 ${{article.published_at}}</span>
                    <span style="margin-right: 15px;">📰 ${{article.source}}</span>
                    <span>📊 可信度: ${{article.credibility_score}}</span>
                </div>
            `;

            // Verification labels
            if (article.verification_labels && article.verification_labels.length > 0) {{
                contentHtml += '<div style="margin-bottom: 15px;">';
                article.verification_labels.forEach(label => {{
                    contentHtml += `<span class="tag" style="background-color: rgba(40, 167, 69, 0.1); color: var(--success-color);">✅ ${{label}}</span>`;
                }});
                contentHtml += '</div>';
            }}

            // Warnings
            if (article.warnings && article.warnings.length > 0) {{
                contentHtml += '<div style="margin-bottom: 15px;">';
                article.warnings.forEach(warn => {{
                    contentHtml += `<div style="color: var(--warning-color);">⚠️ ${{warn}}</div>`;
                }});
                contentHtml += '</div>';
            }}

            // Content
            if (article.content_zh) {{
                contentHtml += `<h4>中文内容</h4><div class="content-box">${{article.content_zh}}</div>`;
            }}
            
            if (article.content) {{
                contentHtml += `<h4>原文内容</h4><div class="content-box">${{article.content}}</div>`;
            }} else {{
                contentHtml += `<p style="color: var(--secondary-text);">暂无内容摘要</p>`;
            }}

            bodyDiv.innerHTML = contentHtml;

            document.getElementById('sourceLink').href = article.url;
            
            document.getElementById('detailModal').style.display = 'flex';
            document.body.style.overflow = 'hidden'; // Prevent scrolling
        }}

        function closeModal(event) {{
            if (event && event.target !== document.getElementById('detailModal') && event.target.className !== 'close-btn') return;
            document.getElementById('detailModal').style.display = 'none';
            document.body.style.overflow = '';
        }}

        // Close modal on Escape key
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Escape') {{
                closeModal();
            }}
        }});

        // Initial render
        renderArticles(articles);
    </script>
</body>
</html>
"""
