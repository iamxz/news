# AGENTS.md

## 项目概述

这是一个运行在命令行中的全球新闻聚合和展示应用。项目每天自动抓取全球热点新闻，并提供中英双语对照展示。

**重要规则：**

- 所有代码注释必须使用中文
- 所有用户界面文本必须使用中文
- 所有文档（包括 README、注释、提交信息等）必须使用中文
- 变量名、函数名、类名使用英文（遵循编程规范）
- 日志输出使用中文
- 错误信息使用中文

## 代码审查智能体 (Code Review Agent)

项目引入了代码审查智能体，旨在确保每次代码改动都符合项目规范和高质量标准。

### 职责

1. **自动校验**：在代码提交或修改后，自动运行静态分析工具（Ruff, Mypy）和测试套件。
2. **规范检查**：
   - 确保所有注释和文档使用中文。
   - 验证命名规范（snake_case, PascalCase）。
   - 检查类型注解是否完整。
3. **逻辑审查**：
   - 检查错误处理是否完善（必须包含中文错误信息）。
   - 验证是否复用了现有的工具函数。
   - 检查是否引入了未使用的依赖。

### 触发方式

- **手动触发**：运行 `Review Changes` 任务。
- **自动建议**：在检测到文件修改后，智能体应主动建议运行审查。

## 目标新闻源列表

### 国际通讯社（最高优先级）

这些通讯社以客观、中立、及时著称，是全球新闻的主要来源：

1. **Reuters（路透社）** - https://www.reuters.com/
   - 全球最大的国际多媒体新闻通讯社
   - 严格遵守新闻独立性和客观性原则
   - RSS: https://www.reuters.com/tools/rss

2. **Associated Press（美联社）** - https://apnews.com/
   - 美国最大的通讯社，全球最可信的新闻来源之一
   - 无党派偏见，以事实报道为核心
   - RSS: https://apnews.com/rss

3. **AFP（法新社）** - https://www.afp.com/
   - 世界三大通讯社之一
   - 多语言新闻服务
   - 注重国际视角

4. **Bloomberg（彭博社）** - https://www.bloomberg.com/
   - 全球领先的商业和金融信息提供商
   - 专注于商业、金融市场和经济新闻
   - RSS: https://feeds.bloomberg.com/markets/news.rss

### 主流权威媒体

4. **BBC News（英国广播公司）** - https://www.bbc.com/news
   - 英国公共广播机构，全球信誉度最高的媒体之一
   - 相对中立和客观
   - RSS: http://feeds.bbci.co.uk/news/rss.xml

5. **The Guardian（卫报）** - https://www.theguardian.com/
   - 英国主流媒体，以深度报道著称
   - 偏自由派但保持新闻专业性
   - RSS: https://www.theguardian.com/world/rss

6. **The New York Times（纽约时报）** - https://www.nytimes.com/
   - 美国最具影响力的报纸
   - 深度调查报道
   - RSS: https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml

7. **The Washington Post（华盛顿邮报）** - https://www.washingtonpost.com/
   - 美国主流媒体，以政治报道著称
   - 曾揭露水门事件

8. **Financial Times（金融时报）** - https://www.ft.com/
   - 全球最权威的财经新闻媒体
   - 侧重商业和经济新闻
   - 国际视角强

9. **The Economist（经济学人）** - https://www.economist.com/
   - 英国新闻周刊，以分析深度著称
   - 覆盖政治、经济、科技等领域
   - RSS: https://www.economist.com/rss

10. **Al Jazeera（半岛电视台）** - https://www.aljazeera.com/
    - 中东地区最有影响力的媒体
    - 提供中东视角的国际新闻
    - RSS: https://www.aljazeera.com/xml/rss/all.xml

### 专业科技新闻

11. **Hacker News** - https://news.ycombinator.com/
    - 科技圈最受欢迎的新闻聚合平台
    - 由 Y Combinator 运营
    - API: https://github.com/HackerNews/API

12. **TechCrunch** - https://techcrunch.com/
    - 科技创业新闻领导者
    - RSS: https://techcrunch.com/feed/

13. **Ars Technica** - https://arstechnica.com/
    - 深度科技新闻和分析
    - RSS: http://feeds.arstechnica.com/arstechnica/index

14. **The Verge** - https://www.theverge.com/
    - 科技、文化、产品评论
    - RSS: https://www.theverge.com/rss/index.xml

### 社交新闻聚合

15. **Reddit World News** - https://www.reddit.com/r/worldnews/
    - 用户驱动的全球新闻讨论
    - API: https://www.reddit.com/dev/api/

16. **Google News** - https://news.google.com/
    - 智能新闻聚合
    - RSS: https://news.google.com/rss

### 中文媒体（可选）

17. **联合早报（Lianhe Zaobao）** - https://www.zaobao.com.sg/
    - 新加坡最权威的华文日报
    - SPH Media（新加坡报业控股）旗下
    - 覆盖新加坡、中国、亚洲及国际新闻
    - 中立客观，专业性强

18. **8视界新闻网（8World）** - https://www.8world.com/
    - 新加坡新传媒（Mediacorp）旗下中文新闻网站
    - 提供本地、区域和国际新闻
    - 包含视频新闻内容

19. **新明日报（Shin Min Daily News）** - https://www.zaobao.com.sg/publication/xin-ming-ri-bao
    - 新加坡通俗华文报纸
    - 关注社会民生新闻
    - 更贴近本地生活

20. **南华早报（SCMP）** - https://www.scmp.com/
    - 香港英文媒体，亚洲视角
    - 提供中英双语内容

21. **端传媒（Initium Media）** - https://theinitium.com/
    - 深度华文媒体
    - 独立调查报道

### 日本媒体

22. **NHK World** - https://www3.nhk.or.jp/nhkworld/en/news/
    - 日本公共广播公司国际频道
    - 提供英文、中文等多语言新闻
    - 日本最权威的新闻机构
    - 中文版：https://www3.nhk.or.jp/nhkworld/zh/news/

23. **The Asahi Shimbun（朝日新闻）** - https://www.asahi.com/ajw/
    - 日本三大报之一，发行量全国第二
    - 英文版提供日本和国际新闻
    - 以进步立场和调查报道著称

24. **The Japan News（读卖新闻）** - https://japannews.yomiuri.co.jp/
    - 读卖新闻集团英文版
    - 读卖新闻是全球发行量最大的报纸
    - 偏保守立场

25. **The Mainichi（每日新闻）** - https://mainichi.jp/english/
    - 日本三大报之一
    - 英文版提供日本国内和国际新闻
    - 较为中立客观

26. **The Japan Times** - https://www.japantimes.co.jp/
    - 日本历史最悠久的英文报纸
    - 独立媒体，非日本大报旗下
    - 深度分析日本社会和政治
    - RSS: https://www.japantimes.co.jp/feed/

### 抓取优先级策略

**高优先级（每小时）：**

- Reuters
- Associated Press
- BBC News
- Hacker News
- Bloomberg

**中优先级（每 6 小时）：**

- The Guardian
- The New York Times
- Al Jazeera
- TechCrunch
- NHK World（日本）
- The Japan Times（日本）

**低优先级（每天一次）：**

- The Economist
- Financial Times
- Ars Technica
- 联合早报（新加坡中文）
- 8视界新闻网（新加坡中文）
- The Asahi Shimbun（日本朝日新闻）
- The Mainichi（日本每日新闻）

### 抓取技术要求

1. **遵守 robots.txt**：尊重网站的爬虫规则
2. **设置合理延迟**：避免对服务器造成压力（建议 1-3 秒）
3. **User-Agent 设置**：使用友好的 User-Agent 标识
4. **优先使用 RSS**：RSS 更稳定且对服务器友好
5. **使用官方 API**：如 Reddit、Hacker News 提供官方 API
6. **错误处理**：网站不可用时自动跳过
7. **去重机制**：避免重复抓取相同新闻
8. **内容清洗**：去除广告、导航等无关内容

## 常用开发命令

### 环境设置

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt

# 更新依赖列表
pip freeze > requirements.txt
```

### 开发和运行

```bash
# 运行应用
python main.py

# 运行应用并显示详细日志
python main.py --verbose

# 开发模式（自动重载）
python -m watchdog main.py
```

### 新闻抓取

```bash
# 手动抓取新闻
python main.py fetch

# 抓取并翻译
python main.py fetch --translate

# 抓取指定新闻源
python main.py fetch --source reddit,hackernews

# 清理旧新闻数据
python main.py clean --days 30
```

### 测试

```bash
# 运行所有测试
pytest

# 运行单个测试文件
pytest tests/test_fetcher.py

# 运行测试并显示覆盖率
pytest --cov=src --cov-report=html

# 运行特定测试
pytest tests/test_fetcher.py::test_reddit_fetch
```

### 代码质量

```bash
# 运行 linter
ruff check .

# 自动修复 lint 问题
ruff check --fix .

# 格式化代码
black .

# 类型检查
mypy src/

# 运行所有代码质量检查
python scripts/check_quality.py
```

## 代码架构

### 目录结构

```
src/
├── fetchers/           # 新闻源抓取器
│   ├── base.py        # 抓取器基类
│   ├── reuters.py     # 路透社抓取
│   ├── ap_news.py     # 美联社抓取
│   ├── bbc.py         # BBC 新闻抓取
│   ├── guardian.py    # 卫报抓取
│   ├── nytimes.py     # 纽约时报抓取
│   ├── aljazeera.py   # 半岛电视台抓取
│   ├── hackernews.py  # Hacker News 抓取
│   ├── bloomberg.py   # 彭博社抓取
│   ├── techcrunch.py  # TechCrunch 抓取
│   ├── reddit.py      # Reddit 抓取
│   ├── zaobao.py      # 联合早报抓取（新加坡中文）
│   ├── eightworld.py  # 8视界抓取（新加坡中文）
│   ├── nhk.py         # NHK World 抓取（日本）
│   ├── asahi.py       # 朝日新闻抓取（日本）
│   ├── japantimes.py  # The Japan Times 抓取（日本）
│   └── __init__.py    # 抓取器聚合
├── validators/         # 新闻验证器
│   ├── base.py        # 验证器基类
│   ├── credibility.py # 可信度评估

│   ├── fact_checker.py  # 事实核查
│   ├── cross_reference.py # 交叉引用验证
│   └── __init__.py    # 验证器聚合
├── translators/        # 翻译服务
│   ├── base.py        # 翻译器基类
│   ├── openai.py      # OpenAI 翻译
│   ├── deepl.py       # DeepL 翻译
│   └── __init__.py    # 翻译器选择
├── display/            # 命令行显示
│   ├── formatter.py   # 格式化输出
│   ├── colors.py      # 颜色主题
│   ├── badges.py      # 标签和徽章显示
│   └── renderer.py    # 渲染引擎
├── storage/            # 数据存储
│   ├── database.py    # 数据库操作
│   ├── cache.py       # 缓存管理
│   └── models.py      # 数据模型
├── scheduler/          # 定时任务
│   ├── cron.py        # 定时调度
│   └── jobs.py        # 任务定义
├── utils/              # 工具函数
│   ├── logger.py      # 日志工具
│   ├── config.py      # 配置管理
│   ├── robots.py      # robots.txt 解析
│   └── helpers.py     # 辅助函数
└── main.py             # 应用入口

tests/                  # 测试文件
├── test_fetchers.py
├── test_translators.py
└── test_integration.py

scripts/                # 脚本文件
├── check_quality.py    # 代码质量检查
└── deploy.sh          # 部署脚本

requirements.txt        # 生产依赖
requirements-dev.txt    # 开发依赖
pyproject.toml         # 项目配置
```

### 核心架构模式

1. **抓取器模式（Fetcher Pattern）**
   - 每个新闻源实现独立的抓取器类
   - 继承自 `BaseFetcher` 基类
   - 统一的接口：`fetch()`, `parse()`, `validate()`
   - 支持错误重试和限流

2. **翻译服务层**
   - 支持多个翻译 API（OpenAI、DeepL 等）
   - 自动选择可用的翻译服务
   - 翻译结果缓存以节省 API 调用
   - 批量翻译优化

3. **命令行渲染**
   - 使用 chalk 进行颜色输出
   - 使用 cli-table3 进行表格展示
   - 支持分页和交互式浏览
   - 响应式布局适配终端宽度

4. **数据流**

   ```
   定时任务 → 抓取器 → 原始数据 → 验证器（可信度/事实核查） → 翻译器 → 双语数据 → 存储 → 展示
   ```

5. **存储策略**
   - SQLite 用于持久化存储
   - Redis 用于缓存和去重
   - 按日期归档历史新闻
   - 自动清理过期数据

### 新闻源集成

每个新闻源需要实现：

- `fetch()`: 获取原始数据
- `parse()`: 解析为统一格式
- `getPriority()`: 返回新闻优先级
- `getCategory()`: 返回新闻分类

统一的新闻数据格式：

```python
{
  'id': str,
  'title': str,
  'title_zh': str,        # 中文标题
  'content': str,
  'content_zh': str,      # 中文内容
  'source': str,          # 新闻源
  'url': str,
  'published_at': datetime,
  'category': str,        # 分类：科技、政治、体育等
  'priority': int,        # 优先级：1-10
  'tags': List[str],

  # 新闻验证字段
  'credibility_score': float,     # 可信度评分：0.0-1.0

  'fact_checked': bool,           # 是否经过事实核查
  'cross_references': int,        # 交叉引用数量（有多少其他来源报道）
  'verification_labels': List[str], # 验证标签列表
  'warnings': List[str],          # 警告信息（如：未经证实、单一来源等）
}
```

### 翻译管理

- 优先使用缓存的翻译结果
- 翻译失败时标记并在下次重试
- 支持批量翻译以提高效率
- 保留原文以便对照阅读
- 专业术语字典确保翻译一致性

### 新闻验证系统

这是项目的核心功能之一，确保用户接收到可信、客观的新闻。

#### 1. 可信度评估（Credibility Assessment）

基于以下维度评估新闻可信度（0.0-1.0）：

- **来源可信度**：基于新闻源的历史信誉
  - 通讯社（Reuters、AP）：0.95-1.0
  - 主流媒体（BBC、NYT）：0.85-0.95
  - 社交聚合（Reddit、HN）：0.60-0.80

- **内容完整性**：
  - 是否包含明确的消息来源
  - 是否有作者署名
  - 是否包含时间、地点等基本要素
  - 是否有引用和链接

- **语言特征**：
  - 情绪化词汇比例（过多情绪词降低评分）
  - 绝对化表述（"绝对"、"肯定"等）
  - 标题党特征（过度夸张）

#### 3. 事实核查（Fact Checking）

**自动核查机制：**

- 检查是否有多个独立来源报道同一事件
- 对比不同来源的关键事实（时间、地点、人物、数据）
- 标记仅有单一来源的新闻
- 识别未经证实的声明

**核查标签：**

- ✅ `已验证`：多个可信来源确认
- ⚠️ `部分验证`：核心事实确认，细节存疑
- ❓ `未经证实`：缺乏独立来源确认
- ⚡ `快讯`：刚发生，等待更多信息
- 🔍 `需要核查`：包含可疑信息

#### 4. 交叉引用验证（Cross-Reference Validation）

- 自动搜索同一事件的不同报道
- 计算交叉引用数量（cross_references）
- 比较不同来源的报道角度
- 识别独家新闻和独立消息

**显示逻辑：**

```python
if cross_references >= 5:
    label = "多源确认"
    color = "green"
elif cross_references >= 3:
    label = "已交叉验证"
    color = "yellow"
elif cross_references == 1:
    label = "单一来源"
    color = "orange"
else:
    label = "独家报道"
    color = "red"
```

#### 5. 验证标签和警告

**验证标签（verification_labels）示例：**

- `高可信度` - credibility_score > 0.85
- `多源证实` - cross_references >= 3
- `官方消息` - 来自政府/官方机构
- `独立调查` - 原创调查报道
- `专家观点` - 包含专家引用

**警告信息（warnings）示例：**

- `⚠️ 单一来源，尚未被其他媒体证实`
- `⚠️ 检测到明显的政治倾向`
- `⚠️ 内容包含未经证实的声明`
- `⚠️ 标题可能存在夸大`
- `⚠️ 情绪化表述较多，建议批判性阅读`
- `⚠️ 来自社交媒体，需谨慎对待`

#### 6. 命令行显示示例

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📰 标题：某国宣布重大政策改革
🌐 来源：Reuters (路透社)
🕒 时间：2026-02-04 10:30

📊 可信度评分：★★★★★ 0.95/1.0
✅ 多源证实 (8个来源)

✅ 高可信度  ✅ 多源证实

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📰 标题：某争议性事件的独家报道
🌐 来源：Reddit
🕒 时间：2026-02-04 08:15

📊 可信度评分：★★★☆☆ 0.62/1.0
⚠️  单一来源 (0个交叉引用)

⚠️ 警告：
  • 单一来源，尚未被其他媒体证实
  • 来自社交媒体，需谨慎对待
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### 7. 验证命令

```bash
# 查看新闻验证详情
python main.py validate --id <news_id>

# 仅显示高可信度新闻（评分 > 0.8）
python main.py show --min-credibility 0.8



# 显示某新闻的交叉引用
python main.py cross-ref --id <news_id>
```

### 命令行交互

- 启动时显示今日热点摘要
- 显示新闻的可信度标签
- 支持分类浏览（科技、政治、财经等）
- 支持按可信度筛选新闻
- 支持关键词搜索
- 支持上下翻页
- 支持详情查看（包含验证信息）
- 支持收藏和标记
- 显示新闻的交叉引用和来源对比

### 定时任务

- 每天凌晨 2 点自动抓取全球新闻
- 每 6 小时检查热点更新
- 每周日清理 30 天前的旧数据
- 每小时检查翻译队列并处理

## 技术栈

### 核心依赖

- Python 3.10+
- SQLite3 - 本地数据库
- Redis - 缓存和去重
- APScheduler - 定时任务调度
- requests - HTTP 请求
- httpx - 异步 HTTP 客户端

### 网页抓取

- BeautifulSoup4 - HTML 解析
- lxml - 高性能 XML/HTML 解析
- Scrapy - 强大的爬虫框架（可选）
- Selenium - 动态网页抓取
- playwright - 现代浏览器自动化
- feedparser - RSS/Atom 订阅解析

### 自然语言处理和验证

- openai - OpenAI API 客户端（用于翻译）
- anthropic - Claude API 客户端（备用）
- transformers - Hugging Face 模型库（可选，本地 NLP）
- spacy - 工业级 NLP 库
- textblob - 简单的情感分析
- scikit-learn - 机器学习工具（用于分类和评分）

### 命令行工具

- rich - 终端美化和表格展示
- click - 命令行参数解析
- colorama - 跨平台颜色支持
- prompt_toolkit - 交互式命令行
- tqdm - 进度条显示

### API 服务

- openai - OpenAI API 客户端
- deepl - DeepL 翻译 API
- praw - Reddit API 客户端
- tweepy - Twitter API 客户端（可选）

### 数据处理

- pandas - 数据分析和处理
- pydantic - 数据验证和设置管理
- python-dateutil - 日期时间处理

### 开发工具

- pytest - 单元测试框架
- pytest-cov - 测试覆盖率
- pytest-asyncio - 异步测试支持
- black - 代码格式化
- ruff - 快速 Python linter
- mypy - 静态类型检查
- pre-commit - Git 提交钩子

## 环境配置

必需的环境变量（在 `.env` 文件中配置）：

```bash
# 翻译 API
OPENAI_API_KEY=your_openai_key
DEEPL_API_KEY=your_deepl_key

# 新闻验证 API（用于偏见检测和事实核查）
OPENAI_MODEL=gpt-4  # 或 gpt-3.5-turbo
CLAUDE_API_KEY=your_claude_key  # 可选，作为备用

# 数据库
DATABASE_PATH=./data/news.db
REDIS_URL=redis://localhost:6379

# 抓取配置
FETCH_INTERVAL=6h
MAX_NEWS_PER_SOURCE=20
NEWS_RETENTION_DAYS=30

# 验证配置
ENABLE_CREDIBILITY_CHECK=true
ENABLE_FACT_CHECK=true
MIN_CREDIBILITY_THRESHOLD=0.5  # 低于此分数会显示警告
CROSS_REF_SEARCH_ENABLED=true

# 代理配置（如需要）
HTTP_PROXY=
HTTPS_PROXY=

# 日志级别
LOG_LEVEL=info
```

## 添加新新闻源

1. 在 `src/fetchers/` 创建新抓取器文件
2. 继承 `BaseFetcher` 并实现必需方法
3. 在 `src/fetchers/__init__.py` 注册新抓取器
4. 添加相应的测试文件
5. 更新配置文件添加新源的设置

示例：

```python
# src/fetchers/example.py
from typing import List, Dict
from .base import BaseFetcher
import requests
from bs4 import BeautifulSoup

class ExampleFetcher(BaseFetcher):
    """示例新闻源抓取器"""

    def __init__(self):
        super().__init__('示例新闻源')
        self.base_url = 'https://example.com'

    async def fetch(self) -> List[Dict]:
        """抓取新闻列表"""
        response = requests.get(f'{self.base_url}/news')
        response.raise_for_status()
        return self.parse(response.text)

    def parse(self, html: str) -> List[Dict]:
        """解析 HTML 并提取新闻数据"""
        soup = BeautifulSoup(html, 'lxml')
        articles = []

        for item in soup.select('.news-item'):
            article = {
                'title': item.select_one('.title').text.strip(),
                'url': item.select_one('a')['href'],
                'published_at': self.parse_date(item.select_one('.date').text),
            }
            articles.append(article)

        return articles
```

## 开发注意事项

### 代码规范

- 所有代码注释使用中文
- 函数和变量名使用 Python snake_case 命名规范
- 类名使用 PascalCase
- 常量使用大写字母和下划线
- 每个模块顶部添加中文文档字符串
- 错误处理必须有中文错误信息
- 使用类型注解（Type Hints）提高代码可读性

### 翻译质量

- 保持新闻专业术语的准确性
- 保留原文链接和引用
- 对于无法翻译的内容保留原文
- 使用术语表确保翻译一致性

### 验证系统准确性

- 定期审查验证算法的准确性
- 收集用户反馈优化评分标准
- 保持验证规则的透明性
- 避免过度依赖单一验证方法
- 对边缘情况进行人工复核

### 性能优化

- 抓取时使用并发控制，避免过载
- 使用缓存减少重复翻译和验证
- 数据库查询使用索引
- 定期清理过期数据
- 批量处理验证任务以减少 API 调用

### 错误处理

- 网络请求必须有重试机制
- API 调用失败要有降级方案（如验证失败仍显示新闻，但标记为"未验证"）
- 数据解析错误要记录并跳过
- 所有错误信息输出中文
- 验证失败不应阻止新闻展示

### 隐私和伦理

- 不收集用户阅读数据
- 不追踪用户行为
- 验证标签要公正、透明
- 避免算法偏见
- 尊重新闻源的版权和 robots.txt

## 部署

### 本地开发

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 配置必要的 API key

# 运行应用
python main.py
```

### 生产部署

```bash
# 安装生产依赖
pip install -r requirements.txt

# 运行应用
python main.py
```

### Docker 部署

```bash
# 构建镜像
docker build -t news-cli .

# 运行容器
docker run -d --env-file .env news-cli

# 使用 docker-compose
docker-compose up -d
```

### 定时任务设置

应用内置 APScheduler 自动运行定时任务，也可以使用系统 cron：

```bash
# 编辑 crontab
crontab -e

# 添加每天凌晨 2 点运行
0 2 * * * cd /path/to/news && /path/to/venv/bin/python main.py fetch --translate

# 每 6 小时更新一次
0 */6 * * * cd /path/to/news && /path/to/venv/bin/python main.py fetch --translate
```
