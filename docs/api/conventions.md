# API 设计规范

## 统一响应格式
```json
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

## 错误码
- `200`: 成功
- `400`: 请求参数错误
- `401`: 未授权
- `500`: 服务器内部错误

## 命名规范
- URL 路径：kebab-case（如 `/api/v1/user-profiles`）
- 参数命名：snake_case 或 camelCase 保持全站统一
