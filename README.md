# 全球新闻聚合 Web 应用

一个现代化的全球新闻聚合 Web 应用。自动抓取全球热点新闻，提供中英双语展示和真实性验证，配备完整的管理后台。

## ✨ 特性

- 🌍 **全球新闻源**：支持路透社、美联社、BBC、华盛顿邮报、金融时报、经济学人、NHK、朝日新闻、南华早报、端传媒等 26 个主流媒体
- 🔄 **自动翻译**：支持 OpenAI、DeepL、Google、百度等多个翻译服务
- ✅ **真实性验证**：
  - 可信度评估（基于来源、内容完整性、语言特征）
  - 事实核查（检查消息来源和具体事实）
  - 交叉引用验证（检查多源报道）
- 🖥️ **Web 界面**：简洁美观的网页界面，支持翻页和筛选
- 🔧 **管理后台**：完整的 /admin 后台管理系统
  - 抓取管理：选择新闻源进行抓取
  - 翻译管理：批量翻译未翻译新闻
  - 验证管理：批量验证新闻可信度
  - 系统设置：数据清理和系统配置
- 🌐 **代理支持**：支持 HTTP/HTTPS/SOCKS5 代理，突破网络限制
- 📊 **数据统计**：实时查看各新闻源统计和翻译验证状态
- 🔍 **灵活筛选**：按来源、分类、可信度、时间筛选新闻

## 📋 目标新闻源

### 国际通讯社
- Reuters（路透社）✅
- Associated Press（美联社）✅
- AFP（法新社）✅
- Bloomberg（彭博社）✅

### 主流媒体
- BBC News ✅
- The Guardian ✅
- The New York Times ✅
- The Washington Post ✅
- Financial Times ✅
- The Economist ✅
- Al Jazeera ✅

### 科技新闻
- Hacker News ✅
- TechCrunch ✅
- Ars Technica ✅
- The Verge ✅
- MIT Technology Review ✅

### 科技博客
- 阮一峰的网络日志 ✅

### 社交聚合
- Reddit ✅
- Google News ✅

### 亚洲媒体
- 联合早报（新加坡）✅
- 8视界（新加坡）✅
- 新明日报（新加坡）✅
- NHK World（日本）✅
- The Japan Times（日本）✅
- Asahi Shimbun（朝日新闻）✅
- Mainichi（每日新闻）✅
- SCMP（南华早报）✅
- 端传媒 ✅

### 中国热搜
- 今日头条热搜 ✅
- 百度热搜 ✅
- 微博热搜 ✅

**全部 31 个新闻源已完成！** 🎉

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

# 如果需要使用代理（可选）：
# HTTP_PROXY=http://127.0.0.1:7890
# HTTPS_PROXY=http://127.0.0.1:7890
```

### 启动应用

```bash
# 启动 Web 服务器
python web_server.py

# 或使用快捷脚本
./start_web.sh
```

然后访问：
- **前台**：http://localhost:4000
- **管理后台**：http://localhost:4000/admin

## 📖 使用指南

### 前台功能

1. **浏览新闻**：首页展示最新新闻列表
2. **筛选新闻**：按来源、分类、可信度、时间筛选
3. **查看详情**：点击新闻查看完整内容和翻译
4. **翻译新闻**：点击翻译按钮翻译单条新闻

### 管理后台功能

访问 http://localhost:4000/admin 进入管理后台

#### 1. 仪表板
- 查看总新闻数、已翻译数、已验证数
- 查看各新闻源统计

#### 2. 抓取管理
- 选择要抓取的新闻源（支持多选）
- 点击"抓取选中的新闻源"开始抓取
- 实时查看抓取进度和结果

#### 3. 翻译管理
- 查看未翻译的新闻列表
- 选择翻译数量（10/50/100条）
- 点击"翻译所有未翻译新闻"批量翻译

#### 4. 验证管理
- 查看未验证的新闻列表
- 批量验证新闻可信度

#### 5. 系统设置
- 清理旧新闻数据
- 查看系统配置信息

## 🏗️ 项目架构

```
src/
├── fetchers/           # 新闻源抓取器（26个）
├── translators/        # 翻译服务
├── validators/         # 新闻验证器
├── storage/            # 数据存储
├── scheduler/          # 定时任务
└── utils/              # 工具函数

templates/              # Web 模板
├── index.html         # 前台首页
├── detail.html        # 新闻详情
└── admin/             # 管理后台
    ├── dashboard.html # 仪表板
    ├── fetch.html     # 抓取管理
    ├── translate.html # 翻译管理
    ├── validate.html  # 验证管理
    └── settings.html  # 系统设置

web_server.py          # Web 应用主程序
requirements.txt       # 依赖列表
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

- [x] 添加更多新闻源（已完成 26/26）✅ 🎉
- [x] 实现定时任务自动抓取 ✅
- [x] 交叉引用验证 ✅
- [x] Web 界面 ✅
- [x] 管理后台 ✅
- [x] 核心主流媒体（华盛顿邮报、金融时报、经济学人）✅
- [x] 补充科技新闻源（Ars Technica、The Verge）✅
- [x] 补充亚洲媒体（8视界、NHK、朝日新闻、每日新闻、Japan Times、新明日报、南华早报、端传媒）✅
- [ ] 添加 Redis 缓存支持
- [ ] 偏见检测器
- [ ] RSS 订阅输出

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系

如有问题，请提交 Issue。
