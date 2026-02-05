# 全球新闻聚合工具

一个运行在命令行中的全球新闻聚合和展示应用。每天自动抓取全球热点新闻，提供中英双语展示和真实性验证。

## ✨ 特性

- 🌍 **全球新闻源**：支持路透社、美联社、BBC、Hacker News 等 26 个主流媒体
- 🔄 **自动翻译**：支持 OpenAI 和 DeepL 自动翻译成中文
- ✅ **真实性验证**：
  - 可信度评估（基于来源、内容完整性、语言特征）

  - 事实核查（检查消息来源和具体事实）
- 🎨 **精美展示**：使用 Rich 库实现彩色命令行界面
- 📊 **数据统计**：查看各新闻源统计和翻译验证状态
- 🔍 **灵活筛选**：按来源、分类、可信度、时间筛选新闻

## 📋 目标新闻源

### 国际通讯社
- Reuters（路透社）
- Associated Press（美联社）
- AFP（法新社）

### 主流媒体
- BBC News、The Guardian、The New York Times
- Financial Times、The Economist、Al Jazeera
- NHK World、The Japan Times 等

### 科技新闻
- Hacker News、TechCrunch、The Verge

### 亚洲媒体
- 联合早报（新加坡）、8视界、朝日新闻（日本）

详见 [AGENTS.md](AGENTS.md)

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Redis（可选，用于缓存）

### 安装

```bash
# 克隆项目
git clone <your-repo-url>
cd news

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加必要的 API key
# 至少需要配置一个翻译 API：
# - OPENAI_API_KEY（推荐）
# - DEEPL_API_KEY
```

### 使用

```bash
# 查看帮助
python main.py --help

# 抓取新闻
python main.py fetch

# 抓取指定新闻源
python main.py fetch -s reuters -s hackernews

# 抓取并立即翻译和验证
python main.py fetch -t -v

# 运行完整流程（抓取 -> 翻译 -> 验证）
python main.py pipeline

# 查看新闻列表
python main.py show

# 查看新闻详情
python main.py detail <news_id>

# 筛选高可信度新闻
python main.py show -m 0.8

# 查看最近 7 天的科技新闻
python main.py show -c 科技 -d 7

# 查看统计信息
python main.py stats

# 翻译未翻译的新闻
python main.py translate

# 验证未验证的新闻
python main.py validate

# 清理 30 天前的旧新闻
python main.py clean
```

## 📖 命令详解

### fetch - 抓取新闻

```bash
python main.py fetch [选项]

选项：
  -s, --source TEXT    指定新闻源（可多选）
  -t, --translate      抓取后立即翻译
  -v, --validate       抓取后立即验证
```

### show - 显示新闻

```bash
python main.py show [选项]

选项：
  -l, --limit INTEGER           显示数量（默认 20）
  -s, --source TEXT            筛选新闻源
  -c, --category TEXT          筛选分类
  -m, --min-credibility FLOAT  最低可信度（0.0-1.0）
  -d, --days INTEGER           最近几天的新闻
```

### pipeline - 完整流程

一键运行抓取、翻译、验证的完整流程：

```bash
python main.py pipeline
```

## 🏗️ 项目架构

```
src/
├── fetchers/           # 新闻源抓取器
│   ├── base.py        # 抓取器基类
│   ├── reuters.py     # 路透社
│   └── hackernews.py  # Hacker News
├── translators/        # 翻译服务
│   ├── openai.py      # OpenAI 翻译
│   └── deepl.py       # DeepL 翻译
├── validators/         # 新闻验证器
│   ├── credibility.py # 可信度评估

│   └── fact_checker.py  # 事实核查
├── storage/            # 数据存储
│   ├── database.py    # SQLite 操作
│   └── models.py      # 数据模型
├── display/            # 命令行显示
│   └── formatter.py   # Rich 格式化
└── utils/              # 工具函数
    ├── logger.py      # 日志
    ├── config.py      # 配置
    └── helpers.py     # 辅助函数
```

## 🔍 验证系统

### 可信度评估

基于以下维度评分（0.0-1.0）：
- **来源可信度**：通讯社 0.95-1.0，主流媒体 0.85-0.95
- **内容完整性**：检查标题、内容、链接、时间
- **语言特征**：检测情绪化、夸张、标题党



### 事实核查

- 检查是否标注消息来源
- 检查是否包含具体事实（数字、日期、地点）
- 标记单一来源新闻

## 📊 显示效果

新闻列表：
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  │ 标题                    │ 来源     │ 可信度  │ 时间
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1  │ Breaking News: ...      │ Reuters  │ ★★★★★  │ 中立  │ 02-04 10:30
2  │ Tech Innovation ...     │ HN       │ ★★★☆☆  │ 中立  │ 02-04 09:15
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

新闻详情：
```
📰 标题

🌐 来源: Reuters
🔗 链接: https://...
🕒 时间: 2026-02-04 10:30:00

📊 验证信息
可信度评分: ★★★★★ 0.95/1.0

✅ 高可信度  ✅ 多源证实

📰 内容
[双语展示]
```

## 🛠️ 开发

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black .
ruff check --fix .
```

### 类型检查

```bash
mypy src/
```

## 📝 待办事项

- [ ] 添加更多新闻源（BBC、Guardian、NYT 等）
- [ ] 实现定时任务自动抓取
- [ ] 添加 Redis 缓存支持
- [ ] 交叉引用验证
- [ ] Web 界面
- [ ] RSS 订阅输出

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系

如有问题，请提交 Issue。
