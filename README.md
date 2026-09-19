# 衣见 AI (YIJIAN AI)

> **基于多模态视觉与个性化推荐的智能穿搭系统**
>
> *《人工智能原理》课程项目*

---

## 📖 项目简介

「衣见 AI」是一个智能穿搭推荐系统。用户上传衣物照片后，系统通过多模态视觉大模型自动识别衣物属性，将其保存到个人数字衣橱；当用户输入穿搭需求（天气、场景、风格）时，**由我们自主设计的推荐算法引擎**进行候选筛选、多因素加权评分与排序，输出 TOP-K 穿搭方案并给出推荐理由。

### 核心数据流

```
用户上传衣物图片
  → 多模态视觉 AI 分析衣物 (感知层)
  → 提取结构化属性 JSON
  → 保存到数字衣橱 (持久化层)
  → 用户输入天气/场景/风格需求
  → 自主推荐算法筛选候选 (决策层)
  → 多因素加权评分 + 排序
  → 输出 TOP-K 穿搭方案 + 推荐理由
```

### AI 与推荐算法解耦设计

| 层级 | 职责 | 技术实现 |
| :--- | :--- | :--- |
| **AI 感知层** | 图像理解、衣物属性识别、自然语言推荐理由生成 | 多模态大模型 API (GPT-4o / 通义千问 / 智谱等) |
| **推荐决策层** | 候选筛选、组合生成、多因素评分、排序 | **团队自主设计实现** (Python) |

---

## 🛠️ 技术栈

| 领域 | 技术 |
| :--- | :--- |
| 前端 | React 18 · TypeScript · Vite · Tailwind CSS · React Router · Axios |
| 后端 | Python 3.12 · FastAPI · Pydantic v2 · SQLAlchemy 2.0 · Uvicorn |
| 数据库 | SQLite (开发) · PostgreSQL (生产可选) |
| AI | 多模态视觉模型 API · LLM API |
| 部署 | Docker · Docker Compose · Nginx |
| CI/CD | GitHub Actions |
| 测试 | pytest · Vitest (计划中) |

---

## 🚀 快速开始

### 前置条件

- Node.js 20+
- Python 3.12+
- Git
- Docker & Docker Compose (可选，用于容器化启动)

### 本地开发 (不使用 Docker)

```bash
# 1. 克隆仓库
git clone <repo-url>
cd AI-Dress

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API Key

# 3. 启动后端
cd apps/api
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. 启动前端 (新终端)
cd apps/web
npm install
npm run dev
```

- 前端：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### Docker 开发环境

```bash
cp .env.example .env
docker compose -f docker-compose.dev.yml up --build
```

---

## 📁 项目结构

```
AI-Dress/
├── apps/
│   ├── web/                 # 前端 (React + Vite + TypeScript)
│   └── api/                 # 后端 (FastAPI + SQLAlchemy)
│       ├── app/
│       │   ├── api/v1/      # API 路由与端点
│       │   ├── core/        # 配置、数据库、统一响应
│       │   ├── models/      # ORM 数据模型
│       │   ├── schemas/     # Pydantic 契约
│       │   └── services/    # 业务逻辑 (VLM、天气、推荐算法)
│       └── tests/           # pytest 测试
├── packages/shared/         # 前后端共享常量
├── docker/                  # Dockerfile & Nginx 配置
├── docs/                    # 项目文档
├── scripts/                 # 运维脚本 (start/stop/deploy/rollback)
├── .github/                 # CI/CD & Issue/PR 模板
├── docker-compose.yml
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── .env.example
└── README.md
```

---

## 🔀 Git 工作流

采用 **Git Flow 轻量变种**，适合 5 人团队协作：

| 分支 | 用途 | 合并规则 |
| :--- | :--- | :--- |
| `main` | 生产稳定版本 | 仅通过 `release/*` PR 合并 |
| `develop` | 日常开发集成 | Feature PR 合并至此 |
| `feature/*` | 功能开发 | 如 `feature/ai-vision` |
| `bugfix/*` | 缺陷修复 | 如 `bugfix/fix-score` |
| `release/*` | 发版准备 | 如 `release/v0.2.0` |

### Commit 规范 (Conventional Commits)

```
feat: add clothing recognition API
fix: fix recommendation score calculation
refactor: simplify wardrobe service
docs: update deployment guide
test: add recommendation scoring tests
chore: update docker config
```

### 版本号 (Semantic Versioning)

`v<主版本>.<次版本>.<修订号>`，如 `v0.1.0`、`v0.2.0`、`v1.0.0`

---

## 🧪 测试

```bash
# 后端测试
cd apps/api
python -m pytest -v

# 前端类型检查
cd apps/web
npm run typecheck

# 前端 Lint
npm run lint
```

---

## 📦 部署

```bash
# 生产环境启动
docker compose -f docker-compose.prod.yml up -d --build

# 停止服务
docker compose -f docker-compose.prod.yml down

# 版本回滚 (通过 Git Tag)
git checkout tags/v0.1.0
docker compose -f docker-compose.prod.yml up -d --build
```

详细部署与回滚文档见 [docs/deployment/](docs/deployment/)。

---

## 🙏 开源致谢

本项目受以下开源项目启发并有所参考：

- **[tandpfun/wardrobe](https://github.com/tandpfun/wardrobe)** — AI 衣橱管理工具 (MIT License)
  - 参考内容：数字衣橱的数据管理理念与 AI 衣物提取概念
  - 本项目自研内容：前后端分离架构、多因素加权推荐算法引擎、天气联动穿搭推荐、容器化部署体系

---

## 📄 许可证

[MIT License](LICENSE)

---

## 👥 团队

YIJIAN AI Team — 《人工智能原理》课程项目组
