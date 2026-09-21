"""
认证相关的请求/响应 Schema。
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class RegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    email: str = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class LoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """登录成功后返回的令牌"""
    access_token: str
    token_type: str = "bearer"


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: str
    created_at: Optional[datetime] = None
