# Docker 部署指南

## 开发环境
使用 `docker-compose.dev.yml`，挂载源码以支持热重载。
```bash
docker compose -f docker-compose.dev.yml up --build
```

## 生产环境
使用 `docker-compose.prod.yml`，服务将通过 Nginx 反向代理。
```bash
./scripts/start.sh
# 或在 Windows 上
.\scripts\start.ps1
```
