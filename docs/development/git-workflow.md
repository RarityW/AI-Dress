# Git 工作流指南

## 分支策略
- `main`: 生产稳定版
- `develop`: 开发主分支
- `feature/*`: 新功能分支
- `fix/*`: 问题修复分支

## 提交规范
使用 Conventional Commits 格式: `type(scope): subject`

## PR 与 Code Review
所有合并至 `develop` 或 `main` 的 PR 均需经过至少一人的 Code Review。

## 标签与版本管理
发布至生产前，应在 `main` 分支上打 `v*` (如 `v1.0.0`) 的 Tag 触发 CD 流水线。
