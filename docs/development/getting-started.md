# 本地开发指南

## 依赖
- Python 3.12+
- Node.js 20+
- Docker

## 步骤
1. Clone 仓库: `git clone ...`
2. 环境配置: `cp .env.example .env` (根据需要修改内容)
3. 启动开发环境: `docker compose -f docker-compose.dev.yml up --build`
4. 访问服务:
   - Web: http://localhost:5173
   - API: http://localhost:8000
