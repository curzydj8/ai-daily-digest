# AI 日报 · ai-daily-digest

每天早上 8 点自动更新的 AI 资讯聚合页，一个页面五个板块。

🌐 在线：https://curzydj8.github.io/ai-daily-digest/

## 五大板块

1. **🏆 开源 AI 工具排行榜** — GitHub 新发布 AI 项目 / 知名 AI 项目 Star 日增长 / HuggingFace 热门模型
2. **📊 GitHub 热门项目榜** — Python / Go / Java / Rust / C# 近 7 天新仓库按 Star 排序
3. **📚 编程学习知识库** — 每日 1 个 Python + 1 个 Go + 1 个 SQL 知识点，历史全部保留，几年后成大型知识库
4. **💬 AI 提示词库** — 每日更新 ChatGPT / Gemini / Muse / 图像生成提示词，按分类整理，点击复制
5. **🧰 AI 工具导航站** — AI 绘图 / 视频 / 配音 / 编程 / 对话工具目录，本周新增标红

## 页面规则

- 每日新建一个页面，左侧日期栏从上到下、新日期在最上
- 点击日期进入当天内容，站内按日期排序新的在前

## 技术

- `fetch_ai.py`：GitHub API（新项目/Star快照/语言榜）+ HuggingFace API（热门模型）+ 本地知识库轮换
- `knowledge/`：Python/Go/SQL 知识点池（各约 30 条，按天轮换）
- `prompts/`：40 条提示词池（4 分类 × 10 条）
- `tools/tools.json`：AI 工具导航注册表（可随时追加，`added` 日期决定"本周新增"）
- `data/YYYY-MM-DD.json`：当日完整日报数据；`data/index.json`：日期索引
