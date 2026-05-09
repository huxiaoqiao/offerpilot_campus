# OfferPilot Campus

面向大学生的 AI 求职操作系统 —— 智联招聘首届全国 AI 创新大赛参赛作品

## 项目简介

OfferPilot Campus 不是"又一个简历修改器"，而是一个将求职全流程串联的决策辅助平台。

**核心价值主张**：让大学生从"盲目海投"变成"证据驱动的精准求职"——每个岗位都给出可解释匹配、简历改写、招聘官视角反馈和下一步行动建议。

### 7 大功能模块

| 模块 | 说明 | 解决痛点 |
|------|------|---------|
| 求职画像 | 上传简历，填写目标岗位/城市/行业/薪资偏好 | 规划无方向 |
| 岗位雷达 | 粘贴/批量导入 JD，自动解析并质量评分 | 招聘信息噪声大 |
| 匹配解释 | 分维度匹配评分 + 证据命中 + 缺口分析 + 改进建议 | 投递无回复 |
| 简历改写 | 针对 JD 一键生成定制简历（STAR 格式） | 简历无头绪 |
| HR 模拟器 | 模拟 HR/ATS 双重视角，输出通过概率和改进建议 | 投递无回复 |
| 面试训练 | 个性化面试题 + STAR 故事 + 风险追问 | 面试准备不足 |
| 求职看板 | Kanban 状态追踪 + 统计面板 + 时间线 | AI 工具碎片化 |

## 技术栈

- **后端**: Python 3.11+ / FastAPI / SQLAlchemy 2.0 async / SQLite
- **前端**: Vite + React 18 + TypeScript + MUI 5 + Tailwind CSS
- **LLM**: OpenAI 兼容接口（支持阿里云 DashScope / Ollama 本地模型）
- **文档解析**: MarkItDown（PDF/DOCX/TXT/Markdown）

## 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- LLM API Key（OpenAI / 阿里云 DashScope / 本地 Ollama 任选其一）

### 1. 启动后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填写至少一个 LLM Provider 的 API Key

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

后端启动后：
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/health

### 2. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用: http://localhost:5173

### 3. 配置 LLM

编辑 `backend/.env`，配置至少一个 LLM Provider：

```env
# 方案 1: OpenAI 兼容接口（推荐）
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4o

# 方案 2: 阿里云 DashScope
ALIYUN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
ALIYUN_API_KEY=sk-xxx
ALIYUN_MODEL=qwen-plus

# 方案 3: Ollama 本地模型
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen2.5:7b
```

## 项目结构

```
software-offerpilot/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI 入口
│   │   ├── config.py         # 配置管理
│   │   ├── database.py       # 数据库引擎
│   │   ├── models/           # SQLAlchemy 模型（7 张表）
│   │   ├── schemas/          # Pydantic Schema
│   │   ├── routers/          # API 路由（44 个端点）
│   │   ├── services/         # 业务逻辑层
│   │   ├── llm/              # LLM 统一客户端
│   │   ├── parser/           # 文档解析器
│   │   ├── prompts/          # Prompt 模板
│   │   └── utils/            # 工具函数
│   ├── data/                 # SQLite 数据库文件
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/            # 7 个功能页面
│   │   ├── components/       # 布局 + 通用组件
│   │   ├── api/              # API 客户端
│   │   ├── store/            # Zustand 状态管理
│   │   └── types/            # TypeScript 类型定义
│   ├── package.json
│   └── vite.config.ts
├── docs/
│   ├── PRD-OfferPilot-Campus.md   # 产品需求文档
│   └── ARCHITECTURE.md            # 系统架构设计
├── scripts/
│   └── start_dev.sh         # 一键启动脚本
└── README.md
```

## API 端点总览

| 模块 | 端点数 | 路径前缀 |
|------|--------|---------|
| 用户画像 | 7 | `/api/profile` |
| 岗位管理 | 7 | `/api/jobs` |
| 匹配评分 | 4 | `/api/match` |
| 简历改写 | 5 | `/api/resume` |
| HR 模拟 | 3 | `/api/hr` |
| 面试训练 | 3 | `/api/interview` |
| 求职看板 | 6 | `/api/dashboard` |

完整 API 文档请访问 http://localhost:8000/docs

## 设计原则

- **不编造**：绝不添加用户简历中不存在的经历、技能或成就
- **不自动投递**：坚持 human-in-the-loop，辅助决策而非替代决策
- **证据驱动**：每个评分、建议都附带可溯源的证据
- **本地优先**：所有数据默认存储在本地 SQLite，保护隐私

## 比赛信息

- **赛事**: 智联招聘首届全国 AI 创新大赛
- **赛道**: AI+求职
- **核心卖点**: 7 模块求职操作系统闭环，HR 模拟器为独创亮点
