# OfferPilot Campus — 系统架构设计文档

> **作者**: 高见远 (Gao) — 架构师  
> **版本**: v1.0  
> **日期**: 2026-05-09  
> **输入文档**: PRD-OfferPilot-Campus.md v1.0  
> **状态**: 初稿

---

## 目录

1. [系统架构总览](#1-系统架构总览)
2. [后端分层架构](#2-后端分层架构)
3. [前端架构](#3-前端架构)
4. [数据模型设计](#4-数据模型设计)
5. [API 接口设计](#5-api-接口设计)
6. [LLM 集成架构](#6-llm-集成架构)
7. [文件清单](#7-文件清单)
8. [任务分解](#8-任务分解)
9. [依赖包列表](#9-依赖包列表)
10. [共享知识与约定](#10-共享知识与约定)
11. [待明确事项](#11-待明确事项)

---

## 1. 系统架构总览

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        浏览器 (Desktop 1280px+)                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │          React SPA (Vite + TypeScript + MUI + Tailwind)    │  │
│  │  ┌─────────┐ ┌────────┐ ┌───────┐ ┌──────┐ ┌──────────┐  │  │
│  │  │Profile  │ │Jobs    │ │Match  │ │Resume│ │Dashboard │  │  │
│  │  │Onboard  │ │Radar   │ │Expl.  │ │Write │ │Board     │  │  │
│  │  └────┬────┘ └───┬────┘ └──┬────┘ └──┬───┘ └────┬─────┘  │  │
│  │       └──────────┴─────────┴─────────┴──────────┘         │  │
│  │                    API Client (axios + SSE)                │  │
│  └────────────────────────┬──────────────────────────────────┘  │
└───────────────────────────┼─────────────────────────────────────┘
                            │ REST API + SSE (流式)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI 后端 (Python 3.11+)                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Router Layer (API路由)                   │  │
│  │  /profile  /jobs  /match  /resume  /hr  /interview  /board│  │
│  └────────────────────────┬──────────────────────────────────┘  │
│  ┌────────────────────────┴──────────────────────────────────┐  │
│  │                   Service Layer (业务逻辑)                  │  │
│  │  ProfileService  JobService  MatchService  ResumeWriter   │  │
│  │  HRSimulator     InterviewService  BoardService           │  │
│  └────────────┬───────────────────────────────┬──────────────┘  │
│  ┌────────────┴────────────┐  ┌───────────────┴──────────────┐  │
│  │   LLM Client (统一)      │  │   Document Parser (MarkItDown)│  │
│  │   - 多 Provider 轮询     │  │   - PDF/DOCX/TXT/MD           │  │
│  │   - JSON Schema 校验     │  │   - 结构化抽取                 │  │
│  │   - SSE 流式输出          │  │                               │  │
│  │   - 重试 + 回退           │  │                               │  │
│  └────────────┬────────────┘  └───────────────┬──────────────┘  │
│  ┌────────────┴───────────────────────────────┴──────────────┐  │
│  │                  Model Layer (数据层)                       │  │
│  │         SQLAlchemy 2.0 Async + SQLite                      │  │
│  │  UserProfile  JobPost  MatchResult  ResumeVersion          │  │
│  │  HRSimulation  InterviewSet  Application                   │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     外部服务                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │OpenAI兼容│  │ 阿里云    │  │ Ollama   │  │ SQLite (本地) │   │
│  │ API      │  │ DashScope│  │ 本地模型  │  │ data/offerpilot.db│
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 架构决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| 前端框架 | Vite + React + TS | 轻量快速，SSR 非 MVP 必需，个人开发效率优先 |
| UI 组件库 | MUI + Tailwind CSS | MUI 提供开箱即用组件，Tailwind 处理自定义样式 |
| 后端框架 | FastAPI async | 原生 async，SSE 支持好，Pydantic 集成 |
| ORM | SQLAlchemy 2.0 async | 异步 ORM，类型提示完善 |
| 数据库 | SQLite | 零部署，本地优先，个人场景无并发问题 |
| 前后端通信 | REST + SSE | REST 做 CRUD，SSE 做 LLM 流式输出 |
| LLM 接口 | OpenAI 兼容 | 统一接口格式，多 Provider 可切换 |

---

## 2. 后端分层架构

### 2.1 分层职责

```
Router (路由层)
  ├── 参数校验 (Pydantic)
  ├── HTTP 方法映射
  ├── SSE 流式端点
  └── 错误响应格式化
      │
Service (业务层)
  ├── 编排多个数据源/外部调用
  ├── LLM prompt 组装与输出校验
  ├── 缓存策略
  └── 业务规则执行
      │
Model (数据层)
  ├── SQLAlchemy ORM 模型
  ├── 数据库 CRUD 操作
  └── 事务管理

LLM Client (独立横切层)
  ├── Provider 管理 (优先级轮询)
  ├── 请求构建 (prompt + schema)
  ├── 流式/非流式调用
  ├── 输出 Pydantic 校验
  └── 重试 + 回退逻辑
```

### 2.2 后端目录结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI 应用入口，挂载路由、中间件、CORS
│   ├── config.py                # 配置管理（环境变量 + .env 文件）
│   ├── database.py              # SQLAlchemy async engine + session 工厂
│   ├── dependencies.py          # FastAPI 依赖注入（DB session 等）
│   │
│   ├── models/                  # SQLAlchemy ORM 模型
│   │   ├── __init__.py
│   │   ├── base.py              # Base 声明、通用 mixin（id, created_at, updated_at）
│   │   ├── profile.py           # UserProfile
│   │   ├── job.py               # JobPost
│   │   ├── match.py             # MatchResult
│   │   ├── resume.py            # ResumeVersion
│   │   ├── hr.py                # HRSimulation
│   │   ├── interview.py         # InterviewSet
│   │   └── application.py       # Application (看板)
│   │
│   ├── schemas/                 # Pydantic 请求/响应 Schema
│   │   ├── __init__.py
│   │   ├── profile.py           # ProfileCreate, ProfileUpdate, ProfileResponse
│   │   ├── job.py               # JobCreate, JobBatchImport, JobResponse
│   │   ├── match.py             # MatchRequest, MatchResponse, DimensionScore
│   │   ├── resume.py            # ResumeRewriteRequest, ResumeRewriteResponse
│   │   ├── hr.py                # HRRequest, HRResponse
│   │   ├── interview.py         # InterviewRequest, InterviewResponse
│   │   ├── application.py       # ApplicationCreate, ApplicationUpdate, BoardStats
│   │   └── common.py            # 分页、通用响应、错误格式
│   │
│   ├── routers/                 # API 路由
│   │   ├── __init__.py
│   │   ├── profile.py           # /api/profile/*
│   │   ├── jobs.py              # /api/jobs/*
│   │   ├── match.py             # /api/match/*
│   │   ├── resume.py            # /api/resume/*
│   │   ├── hr_simulator.py      # /api/hr/*
│   │   ├── interview.py         # /api/interview/*
│   │   ├── dashboard.py         # /api/dashboard/*
│   │   └── llm_proxy.py         # /api/llm/config — LLM 配置管理
│   │
│   ├── services/                # 业务逻辑
│   │   ├── __init__.py
│   │   ├── profile_service.py   # 简历解析 + 用户画像管理
│   │   ├── job_service.py       # JD 解析 + 岗位管理 + 去重 + 评分
│   │   ├── match_service.py     # 匹配评分引擎
│   │   ├── resume_service.py    # 简历改写引擎
│   │   ├── hr_service.py        # HR 模拟引擎
│   │   ├── interview_service.py # 面试训练引擎
│   │   └── board_service.py     # 看板业务逻辑
│   │
│   ├── llm/                     # LLM 集成层
│   │   ├── __init__.py
│   │   ├── client.py            # 统一 LLM 客户端（多 Provider + 重试 + 回退）
│   │   ├── providers.py         # Provider 配置与实例化
│   │   └── output_parser.py     # LLM 输出 → Pydantic 校验 + 重试
│   │
│   ├── parser/                  # 文档解析
│   │   ├── __init__.py
│   │   ├── resume_parser.py     # 简历解析 (MarkItDown + LLM 结构化)
│   │   └── jd_parser.py         # JD 结构化解析 (LLM)
│   │
│   ├── prompts/                 # Prompt 模板（字符串文件）
│   │   ├── __init__.py
│   │   ├── resume_extract.py    # 简历结构化抽取 prompt
│   │   ├── jd_extract.py        # JD 结构化抽取 prompt
│   │   ├── match_score.py       # 匹配评分 prompt
│   │   ├── resume_rewrite.py    # 简历改写 prompt
│   │   ├── hr_simulate.py       # HR 模拟 prompt
│   │   └── interview_gen.py     # 面试题生成 prompt
│   │
│   └── utils/                   # 工具函数
│       ├── __init__.py
│       ├── file_utils.py        # 文件读取、格式检测
│       ├── id_utils.py          # UUID 生成
│       └── text_utils.py        # 文本清洗、截断
│
├── data/                        # SQLite 数据库文件目录
│   └── .gitkeep
├── tests/                       # 测试（MVP 后期补充）
│   └── .gitkeep
├── requirements.txt
├── .env.example                 # 环境变量示例
└── alembic.ini                  # 数据库迁移配置（可选）
```

---

## 3. 前端架构

### 3.1 路由与组件结构

```
frontend/
├── index.html
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.ts
├── postcss.config.js
├── package.json
│
├── src/
│   ├── main.tsx                 # 入口
│   ├── App.tsx                  # 根组件（路由 + 布局）
│   ├── vite-env.d.ts
│   │
│   ├── api/                     # API 客户端
│   │   ├── index.ts             # axios 实例 + 拦截器
│   │   ├── profile.ts           # 用户画像 API
│   │   ├── jobs.ts              # 岗位 API
│   │   ├── match.ts             # 匹配 API
│   │   ├── resume.ts            # 简历改写 API
│   │   ├── hr.ts                # HR 模拟器 API
│   │   ├── interview.ts         # 面试训练 API
│   │   ├── dashboard.ts         # 看板 API
│   │   └── sse.ts               # SSE 流式客户端工具
│   │
│   ├── components/              # 共享组件
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx    # 主布局（侧边栏 + 主内容区）
│   │   │   ├── Sidebar.tsx      # 左侧导航栏
│   │   │   └── Header.tsx       # 顶部导航栏
│   │   ├── common/
│   │   │   ├── ScoreGauge.tsx   # 分数环形图
│   │   │   ├── ScoreBadge.tsx   # 分数标签（颜色编码）
│   │   │   ├── StatusChip.tsx   # 状态标签
│   │   │   ├── LoadingOverlay.tsx
│   │   │   ├── ErrorAlert.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   ├── ConfirmDialog.tsx
│   │   │   └── StreamingText.tsx  # SSE 流式文本渲染
│   │   └── charts/
│   │       ├── RadarChart.tsx   # 雷达图（技能/维度分布）
│   │       └── KanbanBoard.tsx  # 看板组件
│   │
│   ├── pages/                   # 页面组件
│   │   ├── ProfilePage.tsx      # /profile — 求职画像 Onboarding
│   │   ├── JobsPage.tsx         # /jobs — 岗位雷达
│   │   ├── MatchPage.tsx        # /match — 匹配解释
│   │   ├── ResumePage.tsx       # /resume — 简历改写
│   │   ├── HRSimulatorPage.tsx  # /hr-simulator — HR 模拟器
│   │   ├── InterviewPage.tsx    # /interview — 面试训练
│   │   └── DashboardPage.tsx    # /dashboard — 求职看板
│   │
│   ├── hooks/                   # 自定义 Hooks
│   │   ├── useProfile.ts        # 用户画像 CRUD
│   │   ├── useJobs.ts           # 岗位 CRUD
│   │   ├── useMatch.ts          # 匹配评分
│   │   ├── useResume.ts         # 简历改写
│   │   ├── useHR.ts             # HR 模拟
│   │   ├── useInterview.ts      # 面试训练
│   │   ├── useDashboard.ts      # 看板
│   │   └── useSSE.ts            # SSE 流式 Hook
│   │
│   ├── types/                   # TypeScript 类型定义
│   │   ├── profile.ts
│   │   ├── job.ts
│   │   ├── match.ts
│   │   ├── resume.ts
│   │   ├── hr.ts
│   │   ├── interview.ts
│   │   └── application.ts
│   │
│   ├── store/                   # 状态管理 (Zustand)
│   │   ├── index.ts             # store 入口
│   │   ├── profileStore.ts      # 用户画像全局状态
│   │   └── appStore.ts          # 应用级状态（当前选中岗位等）
│   │
│   └── theme/                   # 主题配置
│       ├── theme.ts             # MUI 主题（蓝色系 #3B82F6）
│       └── palette.ts           # 配色方案
│
├── public/
│   └── favicon.ico
└── .env.example
```

### 3.2 路由设计

| 路径 | 页面 | 说明 |
|------|------|------|
| `/` | DashboardPage | 首页/求职看板 |
| `/profile` | ProfilePage | 求职画像 Onboarding |
| `/jobs` | JobsPage | 岗位雷达列表 |
| `/jobs/:id` | JobsPage (详情) | 岗位详情 |
| `/match/:jobId` | MatchPage | 匹配解释（按岗位） |
| `/resume/:jobId` | ResumePage | 简历改写（按岗位） |
| `/hr-simulator/:jobId` | HRSimulatorPage | HR 模拟器（按岗位） |
| `/interview/:jobId` | InterviewPage | 面试训练（按岗位） |
| `/dashboard` | DashboardPage | 求职看板 |

### 3.3 前后端通信

```
普通 CRUD ──→ axios → REST API (JSON)
LLM 生成  ──→ EventSource/fetch → SSE endpoint → 流式 JSON 块
文件上传  ──→ FormData → multipart/form-data → REST API
```

**SSE 流式协议**：

```
POST /api/match/stream
Content-Type: application/json

请求体: { "job_id": "xxx" }

响应: text/event-stream
data: {"type": "progress", "content": "正在分析简历..."}
data: {"type": "chunk", "field": "dimension_scores.skills", "content": "70"}
data: {"type": "chunk", "field": "matched_evidence", "content": "[...]"}
data: {"type": "done", "content": {完整结构化结果}}
```

---

## 4. 数据模型设计

### 4.1 ER 关系图

```
UserProfile (1) ──── (N) JobPost
     │                    │
     │                    ├── (N) MatchResult
     │                    ├── (N) ResumeVersion
     │                    ├── (N) HRSimulation
     │                    ├── (N) InterviewSet
     │                    └── (N) Application
     │
     └── resume_structured (JSON, 结构化简历)
```

### 4.2 SQLAlchemy ORM 模型

#### 4.2.1 通用基础 (base.py)

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class UUIDMixin:
    id: str = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
```

#### 4.2.2 UserProfile (profile.py)

```python
class UserProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_profiles"

    # 基本信息
    name = Column(String(100), nullable=False)
    school = Column(String(200), nullable=False)
    major = Column(String(200), nullable=False)
    grade = Column(String(50), nullable=False)              # 大四/研三等
    graduation_year = Column(Integer, nullable=False)

    # 求职偏好（JSON 存储）
    target_positions = Column(JSON, default=list)            # ["产品经理","数据分析师"]
    target_cities = Column(JSON, default=list)               # ["北京","上海"]
    salary_min = Column(Integer, nullable=True)              # 元/月
    salary_max = Column(Integer, nullable=True)
    target_industries = Column(JSON, default=list)           # ["互联网","金融"]
    avoid_items = Column(JSON, default=list)                 # ["不接受996"]

    # 简历数据
    resume_raw_text = Column(Text, default="")               # 简历原文
    resume_structured = Column(JSON, default=dict)           # 结构化简历（见 Schema）
    resume_filename = Column(String(500), nullable=True)     # 原始文件名

    # 技能自评
    skill_ratings = Column(JSON, default=dict)               # {"Python": 4, "SQL": 3}
```

#### 4.2.3 JobPost (job.py)

```python
class JobPost(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "job_posts"

    user_id = Column(String(36), ForeignKey("user_profiles.id"), nullable=False)

    # 基本信息
    company_name = Column(String(200), nullable=False)
    position_title = Column(String(200), nullable=False)
    jd_raw_text = Column(Text, nullable=False)               # JD 原文

    # 结构化解析结果
    responsibilities = Column(JSON, default=list)            # ["负责...","参与..."]
    hard_requirements = Column(JSON, default=list)           # ["本科以上","熟悉Python"]
    soft_requirements = Column(JSON, default=list)           # ["有团队协作经验"]
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    city = Column(String(100), default="")
    industry = Column(String(100), default="")
    keywords = Column(JSON, default=list)                    # ["Python","数据分析"]
    source_url = Column(String(500), nullable=True)

    # 评分
    quality_score = Column(Integer, default=0)               # 1-100
    quality_details = Column(JSON, default=dict)             # 评分明细

    # 风险与去重
    risk_tags = Column(JSON, default=list)                   # ["薪资异常高","JD模糊"]
    is_duplicate = Column(Boolean, default=False)
    duplicate_of = Column(String(36), nullable=True)         # 原岗位 ID

    # 关系
    user = relationship("UserProfile", backref="job_posts")
```

#### 4.2.4 MatchResult (match.py)

```python
class MatchResult(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "match_results"

    user_id = Column(String(36), ForeignKey("user_profiles.id"), nullable=False)
    job_id = Column(String(36), ForeignKey("job_posts.id"), nullable=False)

    total_score = Column(Integer, default=0)                 # 1-100
    opportunity_level = Column(String(50), default="")       # 强力推荐/值得尝试/需要提升/暂不建议
    dimension_scores = Column(JSON, default=dict)            # {education: {score, detail}, ...}
    matched_evidence = Column(JSON, default=list)            # [{jd_requirement, resume_evidence, source, strength}]
    gaps = Column(JSON, default=list)                        # [{jd_requirement, severity, suggestion}]
    risks = Column(JSON, default=list)                       # [{risk, level, mitigation}]
    improvement_actions = Column(JSON, default=list)         # ["建议1", "建议2"]

    # 关系
    user = relationship("UserProfile")
    job = relationship("JobPost", backref="match_results")
```

#### 4.2.5 ResumeVersion (resume.py)

```python
class ResumeVersion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "resume_versions"

    user_id = Column(String(36), ForeignKey("user_profiles.id"), nullable=False)
    job_id = Column(String(36), ForeignKey("job_posts.id"), nullable=False)

    version = Column(Integer, default=1)
    sections = Column(JSON, default=dict)                    # {summary, skills, experiences, job_intention}
    html_preview = Column(Text, default="")                  # 完整 HTML 简历
    changes_summary = Column(JSON, default=list)             # [{field, action, reason}]

    # 关系
    user = relationship("UserProfile")
    job = relationship("JobPost", backref="resume_versions")
```

#### 4.2.6 HRSimulation (hr.py)

```python
class HRSimulation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "hr_simulations"

    user_id = Column(String(36), ForeignKey("user_profiles.id"), nullable=False)
    job_id = Column(String(36), ForeignKey("job_posts.id"), nullable=False)

    ats_check = Column(JSON, default=dict)                   # {keyword_match_rate, format_compliance, readability_score, issues}
    screening_result = Column(JSON, default=dict)            # {pass_probability, pass_reasons, fail_reasons}
    hr_feedback = Column(JSON, default=list)                 # [{category, feedback, priority}]

    # 关系
    user = relationship("UserProfile")
    job = relationship("JobPost", backref="hr_simulations")
```

#### 4.2.7 InterviewSet (interview.py)

```python
class InterviewSet(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "interview_sets"

    user_id = Column(String(36), ForeignKey("user_profiles.id"), nullable=False)
    job_id = Column(String(36), ForeignKey("job_posts.id"), nullable=False)

    questions = Column(JSON, default=list)                   # [{id, category, question, reference_answer_framework, related_resume_item, related_risk}]
    star_stories = Column(JSON, default=list)                # [{title, situation, task, action, result, applicable_questions}]
    risk_followups = Column(JSON, default=list)              # [{risk, possible_question, suggested_answer}]

    # 关系
    user = relationship("UserProfile")
    job = relationship("JobPost", backref="interview_sets")
```

#### 4.2.8 Application (application.py)

```python
class Application(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "applications"

    user_id = Column(String(36), ForeignKey("user_profiles.id"), nullable=False)
    job_id = Column(String(36), ForeignKey("job_posts.id"), nullable=False, unique=True)

    status = Column(String(50), default="待评估")            # 状态机见下
    match_score = Column(Integer, nullable=True)
    resume_version_id = Column(String(36), ForeignKey("resume_versions.id"), nullable=True)
    next_action = Column(String(500), nullable=True)         # 下一步行动建议
    next_action_deadline = Column(Date, nullable=True)
    notes = Column(Text, default="")
    tags = Column(JSON, default=list)                        # 自定义标签
    timeline = Column(JSON, default=list)                    # [{time, action, detail}]

    # 关系
    user = relationship("UserProfile")
    job = relationship("JobPost", backref="application", uselist=False)
    resume_version = relationship("ResumeVersion", foreign_keys=[resume_version_id])
```

**Application 状态机**：

```
待评估 ──→ 已评估 ──→ 准备中 ──→ 已投递 ──→ 面试中 ──→ 已offer
  │          │          │          │          │
  └─→ 放弃   └─→ 放弃   └─→ 放弃   └─→ 已拒绝  └─→ 已拒绝

合法转换:
  待评估 → 已评估, 放弃
  已评估 → 准备中, 放弃
  准备中 → 已投递, 放弃
  已投递 → 面试中, 已拒绝
  面试中 → 已offer, 已拒绝
  终态: 已offer, 已拒绝, 放弃
```

### 4.3 Pydantic Schema 设计

#### 4.3.1 通用 Schema (schemas/common.py)

```python
from pydantic import BaseModel
from typing import Any

class ApiResponse(BaseModel):
    success: bool = True
    data: Any = None
    message: str = ""

class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int

class ErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    message: str
    detail: Any = None
```

#### 4.3.2 简历结构化 Schema (schemas/profile.py 内)

```python
class EducationItem(BaseModel):
    school: str
    major: str
    degree: str  # 本科|硕士|博士
    start_date: str  # YYYY-MM
    end_date: str
    gpa: str | None = None

class ExperienceItem(BaseModel):
    type: str  # 实习|项目|竞赛|社团
    title: str
    organization: str
    start_date: str
    end_date: str
    description: str
    achievements: list[str] = []
    technologies: list[str] = []

class StructuredResume(BaseModel):
    education: list[EducationItem] = []
    skills: list[str] = []
    experiences: list[ExperienceItem] = []
    honors: list[str] = []
    self_intro: str = ""

class ProfileCreate(BaseModel):
    name: str
    school: str
    major: str
    grade: str
    graduation_year: int
    target_positions: list[str] = []
    target_cities: list[str] = []
    salary_min: int | None = None
    salary_max: int | None = None
    target_industries: list[str] = []
    avoid_items: list[str] = []

class ProfileResponse(ProfileCreate):
    id: str
    resume_structured: StructuredResume
    skill_ratings: dict[str, int]
    created_at: str
    updated_at: str
```

#### 4.3.3 JD 结构化 Schema (schemas/job.py 内)

```python
class JobCreate(BaseModel):
    jd_raw_text: str
    source_url: str | None = None

class JobBatchImport(BaseModel):
    jobs: list[JobCreate]

class JobResponse(BaseModel):
    id: str
    company_name: str
    position_title: str
    jd_raw_text: str
    responsibilities: list[str]
    hard_requirements: list[str]
    soft_requirements: list[str]
    salary_min: int | None
    salary_max: int | None
    city: str
    industry: str
    keywords: list[str]
    quality_score: int
    quality_details: dict
    risk_tags: list[str]
    is_duplicate: bool
    status: str  # 关联 Application 状态
    created_at: str
```

#### 4.3.4 匹配结果 Schema (schemas/match.py 内)

```python
class DimensionScore(BaseModel):
    score: int  # 1-100
    detail: str

class MatchedEvidence(BaseModel):
    jd_requirement: str
    resume_evidence: str
    evidence_source: str  # "简历-项目经历-第2项"
    strength: str  # 强|中|弱

class Gap(BaseModel):
    jd_requirement: str
    severity: str  # 高|中|低
    suggestion: str

class Risk(BaseModel):
    risk: str
    level: str  # 高|中|低
    mitigation: str

class MatchResponse(BaseModel):
    job_id: str
    total_score: int
    opportunity_level: str
    dimension_scores: dict[str, DimensionScore]
    matched_evidence: list[MatchedEvidence]
    gaps: list[Gap]
    risks: list[Risk]
    improvement_actions: list[str]
```

#### 4.3.5 简历改写 Schema (schemas/resume.py 内)

```python
class SkillChange(BaseModel):
    skill: str
    action: str  # 置顶|新增|移除|重排序
    reason: str

class ExperienceRewrite(BaseModel):
    original: str
    rewritten: str
    changes: list[str]

class ResumeSections(BaseModel):
    summary: dict  # {content, source}
    skills: dict   # {content: list[str], changes: list[SkillChange]}
    experiences: list[ExperienceRewrite]
    job_intention: dict  # {content, source}

class ResumeRewriteResponse(BaseModel):
    job_id: str
    version: int
    sections: ResumeSections
    html_preview: str
```

#### 4.3.6 HR 模拟 Schema (schemas/hr.py 内)

```python
class ATSCheck(BaseModel):
    keyword_match_rate: float  # 0-1
    format_compliance: bool
    readability_score: int  # 1-100
    issues: list[str]

class ScreeningResult(BaseModel):
    pass_probability: int  # 0-100
    pass_reasons: list[str]
    fail_reasons: list[str]

class HRFeedback(BaseModel):
    category: str  # 技能|经历|格式|其他
    feedback: str
    priority: str  # 高|中|低

class HRResponse(BaseModel):
    job_id: str
    ats_check: ATSCheck
    screening_result: ScreeningResult
    hr_feedback: list[HRFeedback]
```

#### 4.3.7 面试训练 Schema (schemas/interview.py 内)

```python
class InterviewQuestion(BaseModel):
    id: str
    category: str  # 自我介绍|行为面试|技术问题|情景模拟|反问环节
    question: str
    reference_answer_framework: str
    related_resume_item: str | None = None
    related_risk: str | None = None

class STARStory(BaseModel):
    title: str
    situation: str
    task: str
    action: str
    result: str
    applicable_questions: list[str]

class RiskFollowup(BaseModel):
    risk: str
    possible_question: str
    suggested_answer: str

class InterviewResponse(BaseModel):
    job_id: str
    questions: list[InterviewQuestion]
    star_stories: list[STARStory]
    risk_followups: list[RiskFollowup]
```

#### 4.3.8 看板 Schema (schemas/application.py 内)

```python
class TimelineEntry(BaseModel):
    time: str
    action: str
    detail: str

class ApplicationCreate(BaseModel):
    job_id: str
    status: str = "待评估"
    next_action: str | None = None
    notes: str = ""
    tags: list[str] = []

class ApplicationUpdate(BaseModel):
    status: str | None = None
    next_action: str | None = None
    next_action_deadline: str | None = None
    notes: str | None = None
    tags: list[str] | None = None

class ApplicationResponse(BaseModel):
    id: str
    job_id: str
    job_title: str
    company_name: str
    status: str
    match_score: int | None
    next_action: str | None
    next_action_deadline: str | None
    notes: str
    tags: list[str]
    timeline: list[TimelineEntry]
    created_at: str
    updated_at: str

class BoardStats(BaseModel):
    total: int
    by_status: dict[str, int]           # {"待评估": 5, "已投递": 3, ...}
    avg_match_score: float
    offer_rate: float                   # 已offer / 总数
    interview_rate: float               # (面试中+已offer) / 已投递
    top_dimension_scores: dict[str, float]  # 各维度平均分
```

---

## 5. API 接口设计

### 5.1 API 总览

基础路径: `/api`

| 模块 | 路径前缀 | 说明 |
|------|----------|------|
| 用户画像 | `/api/profile` | 简历上传、偏好管理 |
| 岗位管理 | `/api/jobs` | JD 导入、解析、列表 |
| 匹配评分 | `/api/match` | 匹配计算、结果获取 |
| 简历改写 | `/api/resume` | 简历生成、版本管理 |
| HR 模拟 | `/api/hr` | HR 模拟运行 |
| 面试训练 | `/api/interview` | 面试题生成 |
| 求职看板 | `/api/dashboard` | 状态管理、统计 |
| LLM 配置 | `/api/llm` | Provider 配置 |

### 5.2 详细接口列表

#### 5.2.1 用户画像 `/api/profile`

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| `POST` | `/api/profile` | 创建用户画像 | `ProfileCreate` | `ProfileResponse` |
| `GET` | `/api/profile/{id}` | 获取画像 | - | `ProfileResponse` |
| `PUT` | `/api/profile/{id}` | 更新画像 | `ProfileUpdate` | `ProfileResponse` |
| `POST` | `/api/profile/{id}/resume/upload` | 上传简历文件 | `multipart/form-data (file)` | `{resume_text, resume_structured}` |
| `PUT` | `/api/profile/{id}/resume/structured` | 手动编辑结构化简历 | `StructuredResume` | `ProfileResponse` |
| `PUT` | `/api/profile/{id}/skill-ratings` | 更新技能自评 | `{skill_ratings: dict}` | `ProfileResponse` |
| `POST` | `/api/profile/{id}/resume/reparse` | 重新解析简历 | - | `{resume_structured}` |

#### 5.2.2 岗位管理 `/api/jobs`

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| `POST` | `/api/jobs` | 导入单个 JD | `JobCreate` | `JobResponse` |
| `POST` | `/api/jobs/batch` | 批量导入 JD | `JobBatchImport` | `list[JobResponse]` |
| `POST` | `/api/jobs/import-csv` | CSV 文件导入 | `multipart/form-data (file)` | `list[JobResponse]` |
| `GET` | `/api/jobs` | 岗位列表 | query: `sort_by, order, city, industry, min_score, page, page_size` | `PaginatedResponse[JobResponse]` |
| `GET` | `/api/jobs/{id}` | 岗位详情 | - | `JobResponse` |
| `DELETE` | `/api/jobs/{id}` | 删除岗位 | - | `ApiResponse` |
| `POST` | `/api/jobs/{id}/reparse` | 重新解析 JD | - | `JobResponse` |

#### 5.2.3 匹配评分 `/api/match`

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| `POST` | `/api/match/{job_id}` | 运行匹配评分 | - | `MatchResponse` |
| `POST` | `/api/match/{job_id}/stream` | 流式匹配评分 | - | SSE stream |
| `GET` | `/api/match/{job_id}` | 获取已有匹配结果 | - | `MatchResponse` |
| `GET` | `/api/match/compare` | 多岗位对比 | query: `job_ids=xxx,yyy` | `list[MatchResponse]` |
| `DELETE` | `/api/match/{job_id}` | 删除匹配结果 | - | `ApiResponse` |

#### 5.2.4 简历改写 `/api/resume`

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| `POST` | `/api/resume/{job_id}` | 生成定制简历 | - | `ResumeRewriteResponse` |
| `POST` | `/api/resume/{job_id}/stream` | 流式生成 | - | SSE stream |
| `GET` | `/api/resume/{job_id}` | 获取最新定制简历 | - | `ResumeRewriteResponse` |
| `GET` | `/api/resume/{job_id}/versions` | 获取所有版本 | - | `list[ResumeRewriteResponse]` |
| `GET` | `/api/resume/{job_id}/html` | 获取 HTML 预览 | - | `text/html` |
| `DELETE` | `/api/resume/{job_id}` | 删除定制简历 | - | `ApiResponse` |

#### 5.2.5 HR 模拟器 `/api/hr`

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| `POST` | `/api/hr/{job_id}` | 运行 HR 模拟 | - | `HRResponse` |
| `POST` | `/api/hr/{job_id}/stream` | 流式模拟 | - | SSE stream |
| `GET` | `/api/hr/{job_id}` | 获取已有模拟结果 | - | `HRResponse` |
| `DELETE` | `/api/hr/{job_id}` | 删除模拟结果 | - | `ApiResponse` |

#### 5.2.6 面试训练 `/api/interview`

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| `POST` | `/api/interview/{job_id}` | 生成面试题 | - | `InterviewResponse` |
| `POST` | `/api/interview/{job_id}/stream` | 流式生成 | - | SSE stream |
| `GET` | `/api/interview/{job_id}` | 获取已有面试题 | - | `InterviewResponse` |
| `DELETE` | `/api/interview/{job_id}` | 删除面试题 | - | `ApiResponse` |

#### 5.2.7 求职看板 `/api/dashboard`

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| `POST` | `/api/dashboard/applications` | 创建申请记录 | `ApplicationCreate` | `ApplicationResponse` |
| `GET` | `/api/dashboard/applications` | 获取所有申请 | query: `status, sort_by` | `list[ApplicationResponse]` |
| `GET` | `/api/dashboard/applications/{id}` | 获取单条申请 | - | `ApplicationResponse` |
| `PUT` | `/api/dashboard/applications/{id}` | 更新申请（状态/备注/标签） | `ApplicationUpdate` | `ApplicationResponse` |
| `PUT` | `/api/dashboard/applications/{id}/status` | 变更状态 | `{status: str}` | `ApplicationResponse` |
| `DELETE` | `/api/dashboard/applications/{id}` | 删除申请 | - | `ApiResponse` |
| `GET` | `/api/dashboard/stats` | 看板统计 | - | `BoardStats` |
| `GET` | `/api/dashboard/timeline` | 全局时间线 | query: `page, page_size` | `PaginatedResponse[TimelineEntry]` |

#### 5.2.8 LLM 配置 `/api/llm`

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| `GET` | `/api/llm/providers` | 获取可用 Provider 列表 | - | `list[ProviderInfo]` |
| `GET` | `/api/llm/status` | 获取当前 Provider 状态 | - | `{active, providers: [...]}` |
| `POST` | `/api/llm/test` | 测试 LLM 连通性 | `{provider?: str}` | `{success, latency, provider}` |

---

## 6. LLM 集成架构

### 6.1 Provider 管理

```python
# app/llm/providers.py

PROVIDER_PRIORITY = ["openai_compatible", "aliyun", "ollama"]

PROVIDER_CONFIGS = {
    "openai_compatible": {
        "base_url": "OPENAI_BASE_URL",
        "api_key": "OPENAI_API_KEY",
        "model": "OPENAI_MODEL",
        "supports_stream": True,
        "supports_json_mode": True,
    },
    "aliyun": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api_key": "ALIYUN_API_KEY",
        "model": "qwen-plus",
        "supports_stream": True,
        "supports_json_mode": True,
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "model": "qwen2.5:7b",
        "supports_stream": True,
        "supports_json_mode": False,  # 用 function calling 替代
    },
}
```

### 6.2 调用流程

```
Service 层调用
    │
    ▼
LLMClient.generate(prompt, response_schema, stream=False)
    │
    ├─ 按优先级选择 Provider
    │   ├─ openai_compatible → 失败 → 重试(最多3次)
    │   │                           ↓ 失败
    │   ├─ aliyun           → 失败 → 重试(最多3次)
    │   │                           ↓ 失败
    │   └─ ollama           → 失败 → 重试(最多3次)
    │                           ↓ 失败
    │                       抛出 LLMUnavailableError
    │
    ├─ 构建请求
    │   ├─ structured output → json_schema / function calling
    │   └─ free text → normal completion
    │
    ├─ 调用 API
    │   ├─ stream=True  → AsyncGenerator[str]
    │   └─ stream=False → str → Pydantic 校验
    │
    └─ 输出校验
        ├─ 通过 → 返回结果
        └─ 失败 → 重试(最多2次，调整 prompt)
```

### 6.3 结构化输出策略

```python
# 方案 A: json_schema mode (优先)
response = client.chat.completions.create(
    model=model,
    messages=[...],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "match_result",
            "schema": MatchResponse.model_json_schema()
        }
    }
)

# 方案 B: function calling (Ollama 兜底)
response = client.chat.completions.create(
    model=model,
    messages=[...],
    tools=[{
        "type": "function",
        "function": {
            "name": "output_match_result",
            "parameters": MatchResponse.model_json_schema()
        }
    }],
    tool_choice={"type": "function", "function": {"name": "output_match_result"}}
)
```

---

## 7. 文件清单

### 7.1 后端文件

```
backend/
├── app/
│   ├── __init__.py                        # [空]
│   ├── main.py                            # [中] FastAPI 入口，挂载路由、CORS、静态文件
│   ├── config.py                          # [小] Settings 类，从 .env 加载配置
│   ├── database.py                        # [小] async engine + session 工厂
│   ├── dependencies.py                    # [小] get_db_session 依赖
│   │
│   ├── models/
│   │   ├── __init__.py                    # [小] 导出所有 model
│   │   ├── base.py                        # [小] Base, UUIDMixin, TimestampMixin
│   │   ├── profile.py                     # [小] UserProfile
│   │   ├── job.py                         # [小] JobPost
│   │   ├── match.py                       # [小] MatchResult
│   │   ├── resume.py                      # [小] ResumeVersion
│   │   ├── hr.py                          # [小] HRSimulation
│   │   ├── interview.py                   # [小] InterviewSet
│   │   └── application.py                 # [小] Application
│   │
│   ├── schemas/
│   │   ├── __init__.py                    # [空]
│   │   ├── common.py                      # [小] ApiResponse, PaginatedResponse, ErrorResponse
│   │   ├── profile.py                     # [中] ProfileCreate, ProfileUpdate, ProfileResponse, StructuredResume
│   │   ├── job.py                         # [中] JobCreate, JobBatchImport, JobResponse
│   │   ├── match.py                       # [中] MatchResponse, DimensionScore, MatchedEvidence, Gap, Risk
│   │   ├── resume.py                      # [中] ResumeRewriteResponse, ResumeSections
│   │   ├── hr.py                          # [小] HRResponse, ATSCheck, ScreeningResult, HRFeedback
│   │   ├── interview.py                   # [中] InterviewResponse, InterviewQuestion, STARStory, RiskFollowup
│   │   └── application.py                 # [中] ApplicationCreate, ApplicationUpdate, ApplicationResponse, BoardStats
│   │
│   ├── routers/
│   │   ├── __init__.py                    # [空]
│   │   ├── profile.py                     # [中] 用户画像路由 (7 个端点)
│   │   ├── jobs.py                        # [中] 岗位管理路由 (7 个端点)
│   │   ├── match.py                       # [中] 匹配评分路由 (5 个端点)
│   │   ├── resume.py                      # [中] 简历改写路由 (6 个端点)
│   │   ├── hr_simulator.py                # [小] HR 模拟路由 (4 个端点)
│   │   ├── interview.py                   # [小] 面试训练路由 (4 个端点)
│   │   ├── dashboard.py                   # [中] 看板路由 (8 个端点)
│   │   └── llm_proxy.py                   # [小] LLM 配置路由 (3 个端点)
│   │
│   ├── services/
│   │   ├── __init__.py                    # [空]
│   │   ├── profile_service.py             # [大] 简历解析编排、画像 CRUD
│   │   ├── job_service.py                 # [大] JD 解析编排、去重、质量评分
│   │   ├── match_service.py               # [大] 匹配评分引擎，prompt 编排
│   │   ├── resume_service.py              # [大] 简历改写引擎，STAR 优化，HTML 生成
│   │   ├── hr_service.py                  # [大] HR 模拟引擎，ATS 检查
│   │   ├── interview_service.py           # [大] 面试题生成引擎
│   │   └── board_service.py               # [中] 看板状态机、统计计算
│   │
│   ├── llm/
│   │   ├── __init__.py                    # [空]
│   │   ├── client.py                      # [大] LLMClient 类，多 Provider 轮询、重试、回退
│   │   ├── providers.py                   # [中] Provider 配置、实例化
│   │   └── output_parser.py               # [中] 输出解析、Pydantic 校验、重试逻辑
│   │
│   ├── parser/
│   │   ├── __init__.py                    # [空]
│   │   ├── resume_parser.py               # [大] MarkItDown 解析 + LLM 结构化抽取
│   │   └── jd_parser.py                   # [大] JD 结构化解析 (LLM)
│   │
│   ├── prompts/
│   │   ├── __init__.py                    # [空]
│   │   ├── resume_extract.py              # [中] 简历结构化抽取 prompt
│   │   ├── jd_extract.py                  # [中] JD 结构化抽取 prompt
│   │   ├── match_score.py                 # [大] 匹配评分 prompt (分维度、证据引用)
│   │   ├── resume_rewrite.py              # [大] 简历改写 prompt (STAR、不编造约束)
│   │   ├── hr_simulate.py                 # [大] HR 模拟 prompt (ATS + HR 双视角)
│   │   └── interview_gen.py               # [大] 面试题生成 prompt
│   │
│   └── utils/
│       ├── __init__.py                    # [空]
│       ├── file_utils.py                  # [小] 文件读取、MIME 检测
│       ├── id_utils.py                    # [小] UUID 生成
│       └── text_utils.py                  # [小] 文本清洗、截断、去重
│
├── data/
│   └── .gitkeep
├── tests/
│   └── .gitkeep
├── requirements.txt
├── .env.example
└── seed_data.py                           # [中] 演示数据初始化脚本
```

### 7.2 前端文件

```
frontend/
├── index.html
├── vite.config.ts                         # [小] Vite 配置，proxy 到后端
├── tsconfig.json                          # [小] TypeScript 配置
├── tailwind.config.ts                     # [小] Tailwind 配置，自定义主题色
├── postcss.config.js                      # [小] PostCSS 配置
├── package.json
├── .env.example
│
├── src/
│   ├── main.tsx                           # [小] React 入口
│   ├── App.tsx                            # [中] 根组件，路由配置 + 全局 Provider
│   ├── vite-env.d.ts                      # [小] Vite 类型声明
│   │
│   ├── api/
│   │   ├── index.ts                       # [小] axios 实例 + baseURL + 拦截器
│   │   ├── profile.ts                     # [中] 用户画像 API 调用
│   │   ├── jobs.ts                        # [中] 岗位 API 调用
│   │   ├── match.ts                       # [中] 匹配 API 调用
│   │   ├── resume.ts                      # [中] 简历改写 API 调用
│   │   ├── hr.ts                          # [小] HR 模拟 API 调用
│   │   ├── interview.ts                   # [小] 面试训练 API 调用
│   │   ├── dashboard.ts                   # [中] 看板 API 调用
│   │   └── sse.ts                         # [中] SSE 流式客户端工具
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx              # [中] 主布局容器
│   │   │   ├── Sidebar.tsx                # [中] 左侧导航栏
│   │   │   └── Header.tsx                 # [小] 顶部栏
│   │   ├── common/
│   │   │   ├── ScoreGauge.tsx             # [中] 环形分数图
│   │   │   ├── ScoreBadge.tsx             # [小] 分数标签
│   │   │   ├── StatusChip.tsx             # [小] 状态标签
│   │   │   ├── LoadingOverlay.tsx         # [小] 加载遮罩
│   │   │   ├── ErrorAlert.tsx             # [小] 错误提示
│   │   │   ├── EmptyState.tsx             # [小] 空状态
│   │   │   ├── ConfirmDialog.tsx          # [小] 确认对话框
│   │   │   └── StreamingText.tsx          # [中] SSE 流式文本渲染
│   │   └── charts/
│   │       ├── RadarChart.tsx             # [大] 雷达图组件
│   │       └── KanbanBoard.tsx            # [大] 看板拖拽组件
│   │
│   ├── pages/
│   │   ├── ProfilePage.tsx                # [大] 求职画像页（分步表单 + 简历上传）
│   │   ├── JobsPage.tsx                   # [大] 岗位雷达页（列表 + 详情 + 批量导入）
│   │   ├── MatchPage.tsx                  # [大] 匹配解释页（分数 + 证据 + 缺口 + 建议）
│   │   ├── ResumePage.tsx                 # [大] 简历改写页（左右对比 + HTML 预览）
│   │   ├── HRSimulatorPage.tsx            # [大] HR 模拟器页（概率 + 理由 + 反馈）
│   │   ├── InterviewPage.tsx              # [大] 面试训练页（题目 + 答案 + STAR）
│   │   └── DashboardPage.tsx              # [大] 求职看板页（Kanban + 统计）
│   │
│   ├── hooks/
│   │   ├── useProfile.ts                  # [中] 用户画像 CRUD Hook
│   │   ├── useJobs.ts                     # [中] 岗位 CRUD Hook
│   │   ├── useMatch.ts                    # [中] 匹配评分 Hook
│   │   ├── useResume.ts                   # [中] 简历改写 Hook
│   │   ├── useHR.ts                       # [小] HR 模拟 Hook
│   │   ├── useInterview.ts                # [小] 面试训练 Hook
│   │   ├── useDashboard.ts                # [中] 看板 Hook
│   │   └── useSSE.ts                      # [中] SSE 流式 Hook
│   │
│   ├── types/
│   │   ├── profile.ts                     # [小] 用户画像 TS 类型
│   │   ├── job.ts                         # [小] 岗位 TS 类型
│   │   ├── match.ts                       # [小] 匹配 TS 类型
│   │   ├── resume.ts                      # [小] 简历改写 TS 类型
│   │   ├── hr.ts                          # [小] HR 模拟 TS 类型
│   │   ├── interview.ts                   # [小] 面试训练 TS 类型
│   │   └── application.ts                 # [小] 看板 TS 类型
│   │
│   ├── store/
│   │   ├── index.ts                       # [小] Zustand store 入口
│   │   ├── profileStore.ts                # [中] 用户画像全局状态
│   │   └── appStore.ts                    # [小] 应用级状态
│   │
│   └── theme/
│       ├── theme.ts                       # [小] MUI 主题配置
│       └── palette.ts                     # [小] 配色方案
│
├── public/
│   └── favicon.ico
└── .env.example
```

### 7.3 项目根目录文件

```
software-offerpilot/
├── README.md                              # [中] 项目说明、运行指南
├── docker-compose.yml                     # [小] 可选容器化
├── .gitignore                             # [小] Git 忽略规则
├── backend/                               # 后端目录
├── frontend/                              # 前端目录
├── data/                                  # 演示数据
│   ├── sample_jds/
│   │   ├── jd_sample_01.txt
│   │   ├── jd_sample_02.txt
│   │   └── jd_batch_sample.csv
│   ├── sample_resumes/
│   │   ├── resume_sample_01.pdf
│   │   └── resume_sample_01.txt
│   └── demo_script.md                     # 演示脚本
├── docs/                                  # 文档目录
│   ├── PRD-OfferPilot-Campus.md
│   ├── ARCHITECTURE.md                    # 本文档
│   └── API.md                             # API 文档（自动生成）
└── scripts/
    ├── start_dev.sh                       # 开发环境一键启动
    └── seed_demo.sh                       # 加载演示数据
```

---

## 8. 任务分解

### 8.1 实现顺序总览

```
Phase 1: 基础设施 (Day 1-2)
  └── T1 ~ T5

Phase 2: 核心数据流 (Day 3-6)
  └── T6 ~ T10

Phase 3: LLM 驱动功能 (Day 7-14)
  └── T11 ~ T17

Phase 4: 前端页面 (Day 10-20)
  └── T18 ~ T26

Phase 5: 集成与打磨 (Day 21-25)
  └── T27 ~ T30

Phase 6: 演示准备 (Day 26-28)
  └── T31 ~ T33
```

### 8.2 详细任务列表

#### Phase 1: 基础设施

| ID | 任务名称 | 涉及文件 | 前置依赖 | 工作量 | 实现要点 |
|----|---------|---------|---------|--------|---------|
| T1 | 后端项目骨架搭建 | `backend/app/main.py`, `config.py`, `database.py`, `requirements.txt`, `.env.example` | 无 | 小 | FastAPI app 创建、CORS、数据库 engine/session、配置管理、健康检查端点 `/api/health` |
| T2 | 数据模型层 | `backend/app/models/*.py` | T1 | 小 | 所有 7 个 SQLAlchemy 模型定义、`create_all` 自动建表 |
| T3 | Pydantic Schema 层 | `backend/app/schemas/*.py` | 无 | 小 | 所有请求/响应 Schema，与模型对齐 |
| T4 | 前端项目骨架搭建 | `frontend/*` (vite.config.ts, package.json, main.tsx, App.tsx, theme/*) | 无 | 小 | Vite + React + TS 初始化、MUI 主题配置（蓝色系 #3B82F6）、Tailwind 集成、react-router 路由 |
| T5 | 前端布局组件 | `frontend/src/components/layout/*` | T4 | 小 | AppLayout（侧边栏+主内容区）、Sidebar 导航、Header 顶部栏、响应式适配 |

#### Phase 2: 核心数据流

| ID | 任务名称 | 涉及文件 | 前置依赖 | 工作量 | 实现要点 |
|----|---------|---------|---------|--------|---------|
| T6 | LLM Client 统一客户端 | `backend/app/llm/client.py`, `providers.py`, `output_parser.py` | T1 | 大 | 多 Provider 管理、优先级轮询、重试 3 次+回退、stream/non-stream、Pydantic 输出校验、function calling / json_schema 双模式 |
| T7 | 简历解析 Service | `backend/app/parser/resume_parser.py`, `prompts/resume_extract.py`, `services/profile_service.py` | T2, T3, T6 | 大 | MarkItDown 读取 PDF/DOCX/TXT/MD → 原文 → LLM 结构化抽取为 StructuredResume → 存入 UserProfile |
| T8 | 用户画像 Router + API | `backend/app/routers/profile.py`, `services/profile_service.py` | T7 | 中 | 7 个端点：CRUD、文件上传、结构化编辑、技能自评 |
| T9 | JD 解析 Service | `backend/app/parser/jd_parser.py`, `prompts/jd_extract.py`, `services/job_service.py` | T2, T3, T6 | 大 | LLM 结构化提取：公司名、岗位名、职责、硬性/软性要求、薪资、城市、关键词；质量评分规则引擎；去重逻辑（标题+公司+薪资相似度） |
| T10 | 岗位管理 Router + API | `backend/app/routers/jobs.py`, `services/job_service.py` | T9 | 中 | 7 个端点：单条/批量导入、CSV 导入、列表筛选排序、详情、删除、重新解析 |

#### Phase 3: LLM 驱动功能

| ID | 任务名称 | 涉及文件 | 前置依赖 | 工作量 | 实现要点 |
|----|---------|---------|---------|--------|---------|
| T11 | 匹配评分引擎 | `backend/app/services/match_service.py`, `prompts/match_score.py` | T6, T7, T9 | 大 | prompt 构建（简历+JD 全文）、分维度评分（教育/技能/经验/项目/软性）、证据命中列表（溯源到简历/JD 位置）、缺口分析、机会等级映射、改进建议 |
| T12 | 匹配 Router + SSE | `backend/app/routers/match.py` | T11 | 中 | 5 个端点：同步评分、SSE 流式评分、获取结果、多岗位对比、删除。SSE 协议：progress → chunk → done |
| T13 | 简历改写引擎 | `backend/app/services/resume_service.py`, `prompts/resume_rewrite.py` | T6, T11 | 大 | 摘要改写（JD 关键词+用户优势）、技能区优化（置顶+补充）、STAR 项目经历重写、不编造约束 prompt、HTML 简历模板生成、版本管理 |
| T14 | 简历改写 Router + SSE | `backend/app/routers/resume.py` | T13 | 中 | 6 个端点：生成、SSE 流式、获取、版本列表、HTML 预览、删除 |
| T15 | HR 模拟引擎 | `backend/app/services/hr_service.py`, `prompts/hr_simulate.py` | T6, T11 | 大 | ATS 检查（关键词匹配率、格式合规、可读性）、HR 视角筛选（通过概率、通过/拒绝理由）、HR 反馈（专业友善语气） |
| T16 | HR 模拟 Router + SSE | `backend/app/routers/hr_simulator.py` | T15 | 中 | 4 个端点：同步运行、SSE 流式、获取结果、删除 |
| T17 | 面试训练引擎 + Router | `backend/app/services/interview_service.py`, `prompts/interview_gen.py`, `backend/app/routers/interview.py` | T6, T11, T15 | 大 | 10-15 道面试题生成（5 类）、参考答案框架、STAR 故事（基于用户真实项目）、风险点追问、4 个 API 端点 |

#### Phase 4: 前端页面

| ID | 任务名称 | 涉及文件 | 前置依赖 | 工作量 | 实现要点 |
|----|---------|---------|---------|--------|---------|
| T18 | 前端 API 层 + SSE 工具 | `frontend/src/api/*.ts`, `frontend/src/types/*.ts` | T3, T4 | 中 | axios 实例、请求/响应拦截器、所有模块 API 函数、SSE EventSource/fetch 封装、TS 类型定义（与后端 Schema 对齐） |
| T19 | 共享组件库 | `frontend/src/components/common/*`, `components/charts/*` | T4 | 中 | ScoreGauge（环形图）、ScoreBadge（颜色编码）、StatusChip、LoadingOverlay、ErrorAlert、EmptyState、ConfirmDialog、StreamingText、RadarChart、KanbanBoard |
| T20 | 求职画像页面 | `frontend/src/pages/ProfilePage.tsx`, `hooks/useProfile.ts` | T18, T19 | 大 | 分步表单（3步：上传→信息→偏好）、拖拽上传区域、解析进度动画、结构化结果可编辑、偏好多选标签、技能自评星级、画像雷达图 |
| T21 | 岗位雷达页面 | `frontend/src/pages/JobsPage.tsx`, `hooks/useJobs.ts` | T18, T19 | 大 | JD 粘贴输入、CSV 批量导入弹窗、MUI DataTable 列表、质量分颜色编码、筛选排序、行展开详情、风险标签展示 |
| T22 | 匹配解释页面 | `frontend/src/pages/MatchPage.tsx`, `hooks/useMatch.ts` | T18, T19 | 大 | 总分卡片 + 机会等级标签、分维度雷达图、证据列表（可溯源）、缺口列表（关联改进建议 + "去改简历"按钮）、SSE 流式渲染 |
| T23 | 简历改写页面 | `frontend/src/pages/ResumePage.tsx`, `hooks/useResume.ts` | T18, T19 | 大 | 左右对比布局（原简历 vs 定制简历）、变更高亮（绿色新增/黄色修改）、每处变更可接受/拒绝、HTML 预览弹窗（支持打印 PDF）、SSE 流式 |
| T24 | HR 模拟器页面 | `frontend/src/pages/HRSimulatorPage.tsx`, `hooks/useHR.ts` | T18, T19 | 中 | 通过概率圆环图、双栏（通过理由 | 拒绝理由）、HR 反馈气泡样式、ATS 问题列表 |
| T25 | 面试训练页面 | `frontend/src/pages/InterviewPage.tsx`, `hooks/useInterview.ts` | T18, 19 | 中 | 左侧题目列表 + 右侧详情、分类颜色标签、参考答案可折叠、STAR 故事卡片、风险追问标记 |
| T26 | 求职看板页面 | `frontend/src/pages/DashboardPage.tsx`, `hooks/useDashboard.ts` | T18, T19 | 大 | Kanban 拖拽（待评估→已评估→准备中→已投递→面试中→已offer/已拒绝）、卡片信息、点击展开详情、统计面板（投递数/面试率/offer率/匹配分分布）、时间线 |

#### Phase 5: 集成与打磨

| ID | 任务名称 | 涉及文件 | 前置依赖 | 工作量 | 实现要点 |
|----|---------|---------|---------|--------|---------|
| T27 | 端到端联调 | 全栈 | T8, T10, T12, T14, T16, T17, T20-T26 | 中 | 完整流程跑通：Onboarding → 岗位导入 → 匹配 → 简历改写 → HR 模拟 → 面试题 → 看板 |
| T28 | 演示数据与种子脚本 | `backend/seed_data.py`, `data/sample_*`, `data/demo_script.md` | T27 | 中 | 3 个典型用户画像（小林/小张/小王）、10 个岗位 JD、预置匹配结果、演示脚本 |
| T29 | 错误处理与边界情况 | 全栈 | T27 | 中 | LLM 失败友好提示、文件解析失败兜底（手动粘贴）、空数据优雅降级、加载状态 |
| T30 | 状态管理与数据流优化 | `frontend/src/store/*`, hooks 优化 | T27 | 小 | Zustand store 完善、缓存策略（已获取的匹配/简历结果不重复请求）、乐观更新 |

#### Phase 6: 演示准备

| ID | 任务名称 | 涉及文件 | 前置依赖 | 工作量 | 实现要点 |
|----|---------|---------|---------|--------|---------|
| T31 | UI 细节打磨 | 所有页面 | T27 | 中 | 加载动画、过渡效果、颜色编码、空状态引导、移动端基础适配 |
| T32 | 启动脚本与 README | `scripts/start_dev.sh`, `README.md`, `docker-compose.yml` | T30 | 小 | 一键启动前后端、环境变量说明、运行指南 |
| T33 | API 文档自动生成 | `docs/API.md` | T27 | 小 | FastAPI 自动生成 OpenAPI spec，导出为 Markdown |

### 8.3 关键路径

```
T1 → T2 → T7 → T8 → T11 → T12 → T13 → T14 → T15 → T16 → T17
         ↗                                          ↘
T6 ──────┘                                            T27 → T28 → T29
         ↘                                          ↗
T4 → T5 → T18 → T19 → T20 ~ T26 ────────────────────┘
```

**并行策略**：
- T1-T5 可全部并行（后端骨架 + 前端骨架互不依赖）
- T6-T10 与 T18-T19 可并行（后端 LLM 层 + 前端 API/组件层）
- T11-T17 与 T20-T26 可并行（后端功能 + 前端页面），但前端页面需要 mock 数据先做

---

## 9. 依赖包列表

### 9.1 后端 `requirements.txt`

```txt
# Web 框架
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
python-multipart>=0.0.9

# 数据库
sqlalchemy[asyncio]>=2.0.30
aiosqlite>=0.20.0

# 数据验证
pydantic>=2.7.0
pydantic-settings>=2.3.0

# LLM 客户端
openai>=1.30.0

# 文档解析
markitdown[all]>=0.0.1

# 工具库
python-dotenv>=1.0.0
python-dateutil>=2.9.0
httpx>=0.27.0

# 文件处理
aiofiles>=24.1.0
```

### 9.2 前端 `package.json` (dependencies)

```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.26.0",
    "@mui/material": "^5.16.0",
    "@mui/icons-material": "^5.16.0",
    "@emotion/react": "^11.13.0",
    "@emotion/styled": "^11.13.0",
    "@mui/x-data-grid": "^7.12.0",
    "axios": "^1.7.0",
    "zustand": "^4.5.0",
    "recharts": "^2.12.0",
    "@dnd-kit/core": "^6.1.0",
    "@dnd-kit/sortable": "^8.0.0",
    "@dnd-kit/utilities": "^3.2.0",
    "react-markdown": "^9.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.5.0",
    "vite": "^5.4.0"
  }
}
```

**选型说明**：
- **recharts**: 雷达图、环形图、柱状图，轻量够用
- **@dnd-kit**: 看板拖拽排序，比 react-beautiful-dnd 更活跃
- **@mui/x-data-grid**: 岗位列表表格，内置排序、筛选、分页
- **zustand**: 轻量状态管理，比 Redux 少样板代码

---

## 10. 共享知识与约定

### 10.1 命名规范

| 类别 | 规范 | 示例 |
|------|------|------|
| Python 文件 | snake_case | `profile_service.py` |
| Python 类 | PascalCase | `UserProfile`, `MatchService` |
| Python 函数/变量 | snake_case | `get_profile()`, `match_score` |
| Python 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| TS/TSX 文件 | camelCase (hooks/utils) 或 PascalCase (组件) | `useProfile.ts`, `ProfilePage.tsx` |
| TS 类型 | PascalCase | `ProfileResponse`, `MatchResult` |
| API 路径 | kebab-case | `/api/jobs/batch-import` |
| 数据库表名 | snake_case 复数 | `user_profiles`, `job_posts` |
| 数据库列名 | snake_case | `created_at`, `quality_score` |
| JSON 字段 | snake_case | `total_score`, `matched_evidence` |

### 10.2 目录结构约定

- **router 层**：只做参数校验和 HTTP 方法映射，不写业务逻辑
- **service 层**：编排业务流程，调用 LLM client、parser、model
- **model 层**：只做数据库 CRUD，不包含业务判断
- **prompt 层**：纯字符串模板，用函数封装参数化构建
- 一个 router 文件对应一个 service 文件（命名对应）

### 10.3 错误处理

```python
# 后端统一错误响应格式
{
    "success": false,
    "error_code": "LLM_TIMEOUT",      # 枚举: LLM_TIMEOUT, LLM_INVALID_OUTPUT, FILE_PARSE_ERROR, NOT_FOUND, VALIDATION_ERROR
    "message": "LLM 服务超时，请稍后重试",
    "detail": { ... }                  # 可选，调试用
}

# HTTP 状态码映射
# 200: 成功
# 201: 创建成功
# 400: 请求参数错误 (VALIDATION_ERROR)
# 404: 资源不存在 (NOT_FOUND)
# 422: Pydantic 校验失败
# 500: 服务器内部错误
# 503: LLM 服务不可用 (LLM_TIMEOUT, LLM_UNAVAILABLE)
```

### 10.4 SSE 流式协议

```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

# 事件类型:
# 1. progress - 进度提示
data: {"type": "progress", "content": "正在解析简历..."}

# 2. chunk - 字段级增量
data: {"type": "chunk", "field": "dimension_scores.skills", "content": "{\"score\": 70}"}

# 3. done - 完成，携带完整结果
data: {"type": "done", "content": {...完整 JSON...}}

# 4. error - 错误
data: {"type": "error", "content": "LLM 调用失败"}
```

### 10.5 数据库约定

- 所有表都有 `id` (UUID)、`created_at`、`updated_at`
- JSON 字段使用 SQLAlchemy 的 `JSON` 类型，SQLite 原生支持
- 外键关系使用 `String(36)` 存储 UUID
- 当前设计为单用户（个人参赛），不做多用户认证，`user_id` 固定为默认用户
- 数据库文件路径: `backend/data/offerpilot.db`

### 10.6 前端约定

- 组件文件使用 PascalCase，一个文件一个组件
- Hooks 使用 `use` 前缀，一个文件一个 hook
- API 调用统一放在 `src/api/` 目录，页面不直接调用 axios
- 类型定义放在 `src/types/`，与后端 Schema 一一对应
- MUI 组件优先，自定义样式用 Tailwind，避免混用过多
- 全局主题色通过 MUI `createTheme` + Tailwind `extend.colors` 双重配置

---

## 11. 待明确事项

以下问题需要与产品经理（许清楚）确认：

### 11.1 数据模型相关

| # | 问题 | 影响范围 | 建议默认值 |
|---|------|---------|-----------|
| Q1 | 用户是否需要登录注册？MVP 阶段是否只支持单用户本地使用？ | 认证模块、数据隔离 | **默认单用户**，不做登录，user_id 固定 |
| Q2 | 简历解析失败后，手动粘贴的文本格式要求是什么？纯文本还是 Markdown？ | 简历解析流程 | **支持纯文本**，LLM 自行结构化 |
| Q3 | 岗位状态 "准备中" 的具体含义？是从"已评估"到"已投递"之间的"正在改简历+准备面试"阶段吗？ | 看板状态机 | **是**，准备中 = 已评估 + 正在改简历/准备面试 |

### 11.2 功能优先级相关

| # | 问题 | 影响范围 | 建议默认值 |
|---|------|---------|-----------|
| Q4 | 匹配评分的维度权重是否固定，还是需要用户自定义？ | 匹配评分引擎 | **固定权重**，MVP 不做自定义 |
| Q5 | 简历改写是否需要支持"拒绝某处改写后 AI 重新生成"？还是只做一次性生成？ | 简历改写交互 | **只做一次性生成**，用户可手动编辑 |
| Q6 | HR 模拟器的"多轮模拟"（严格型/宽松型）是否 P1？ | HR 模拟器功能范围 | **P1**，MVP 只做默认 HR 风格 |
| Q7 | 面试训练的"练习记录"（已练/需加强/已掌握）是否 P1？ | 面试训练功能范围 | **P1**，MVP 只做题目生成 |

### 11.3 UI/UX 相关

| # | 问题 | 影响范围 | 建议默认值 |
|---|------|---------|-----------|
| Q8 | 前端路由是否需要 URL hash 路由（`#/profile`）还是 history 路由（`/profile`）？ | 路由配置 | **history 路由**，Vite dev server 自带支持 |
| Q9 | 看板拖拽排序是否需要持久化顺序？ | 看板存储 | **按状态分组**，组内按创建时间排序，不做拖拽排序持久化 |
| Q10 | 简历改写的"左右对比"是分屏对比还是 Tab 切换？ | 简历改写 UI | **左右分屏**，50/50 分配 |

### 11.4 技术相关

| # | 问题 | 影响范围 | 建议默认值 |
|---|------|---------|-----------|
| Q11 | CSV 批量导入的 JD 字段格式要求？至少需要哪些字段？ | CSV 导入 | **至少**: 公司名、岗位名、JD 文本；可选: 来源链接、城市 |
| Q12 | HTML 简历预览是否需要支持自定义模板（如不同风格的简历模板）？ | 简历 HTML 生成 | **MVP 只做一套模板**，风格简洁专业 |
| Q13 | 是否需要数据导出/备份功能（导出用户数据为 JSON）？ | 看板功能 | **P1**，MVP 不做 |
| Q14 | "下一步行动建议"是 AI 自动生成还是手动填写？ | 看板功能 | **AI 自动生成**（基于当前状态+匹配结果），用户可编辑 |

---

## 附录 A: 状态码枚举

```python
# Application 状态
APPLICATION_STATUSES = [
    "待评估",    # 新导入的岗位
    "已评估",    # 已完成匹配评分
    "准备中",    # 正在改简历/准备面试
    "已投递",    # 已提交申请
    "面试中",    # 获得面试机会
    "已offer",   # 收到 offer
    "已拒绝",    # 被拒绝
    "放弃",      # 主动放弃
]

# 机会等级
OPPORTUNITY_LEVELS = {
    "强力推荐": (80, 100),
    "值得尝试": (60, 79),
    "需要提升": (40, 59),
    "暂不建议": (0, 39),
}

# 证据强度
EVIDENCE_STRENGTHS = ["强", "中", "弱"]

# 风险等级
RISK_LEVELS = ["高", "中", "低"]

# HR 反馈优先级
HR_PRIORITIES = ["高", "中", "低"]

# 面试题分类
QUESTION_CATEGORIES = [
    "自我介绍",
    "行为面试",
    "技术问题",
    "情景模拟",
    "反问环节",
]
```

## 附录 B: LLM 错误码

```python
class LLMErrorCode:
    TIMEOUT = "LLM_TIMEOUT"              # 请求超时
    RATE_LIMITED = "LLM_RATE_LIMITED"    # 频率限制
    INVALID_OUTPUT = "LLM_INVALID_OUTPUT" # 输出不符合 Schema
    PROVIDER_UNAVAILABLE = "LLM_PROVIDER_UNAVAILABLE"  # 所有 Provider 不可用
    PARSE_ERROR = "LLM_PARSE_ERROR"      # JSON 解析失败
```

## 附录 C: 文件大小标记说明

| 标记 | 预估行数 | 说明 |
|------|---------|------|
| 小 | < 100 行 | 配置、简单模型、简单 Schema |
| 中 | 100-300 行 | Router、Hook、组件、中等 Service |
| 大 | 300-600 行 | 核心 Service（LLM 编排）、页面组件、LLM Client |
