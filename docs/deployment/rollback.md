# 版本回滚 SOP

## Git Tag 回滚
若代码需要回退，使用 `git revert` 或重新指定 Tag。

## Docker 镜像回滚
若线上出现紧急情况，使用回滚脚本指定稳定的版本号：
```bash
./scripts/rollback.sh v1.0.0
# 或 Windows 下
.\scripts\rollback.ps1 v1.0.0
```
