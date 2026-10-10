"""
认证相关的请求/响应 Schema。
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class RegisterRequest(BaseModel):
    """用户注册请求：使用专属账号 (account) 与密码绑定，用户名 (username) 仅作为展示昵称"""
    account: Optional[str] = Field(None, min_length=2, max_length=50, description="登录账号（用于与密码关联进行系统鉴权）")
    username: Optional[str] = Field(None, min_length=1, max_length=50, description="用户昵称/姓名（仅用于页面显示，不作为登录凭据）")
    email: str = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, max_length=128, description="登录密码")


class LoginRequest(BaseModel):
    """用户登录请求：使用账号 (account) 或邮箱与密码验证登录，用户名不用作登录账号"""
    account: Optional[str] = Field(None, description="登录账号或邮箱")
    username: Optional[str] = Field(None, description="兼容别名，当 account 为空时作为后备账号传参")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """登录成功后返回的令牌"""
    access_token: str
    token_type: str = "bearer"


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    account: str
    username: str
    email: str
    created_at: Optional[datetime] = None
