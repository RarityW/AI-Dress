"""
用户认证 API 端点：注册、登录、当前用户信息。
"""
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.response import ApiResponse, success_response, error_response
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.models.user import User
from app.models.preference import UserPreference
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserInfoResponse,
)

router = APIRouter()


@router.post("/register", response_model=ApiResponse[TokenResponse])
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    """
    用户注册：创建用户、哈希密码、初始化默认偏好并直接签发 JWT 访问令牌。
    """
    # 校验用户名是否已存在
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response(code=400, message="用户名已存在").model_dump(),
        )

    # 校验邮箱是否已存在
    existing_email = db.query(User).filter(User.email == request.email).first()
    if existing_email:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response(code=400, message="邮箱已被注册").model_dump(),
        )

    # 创建新用户
    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 初始化默认偏好
    default_pref = UserPreference(
        user_id=new_user.id,
        preferred_styles=[],
        avoided_colors=[],
        custom_weights={},
    )
    db.add(default_pref)
    db.commit()

    # 签发 JWT
    access_token = create_access_token(data={"sub": new_user.username})
    return success_response(
        data=TokenResponse(access_token=access_token, token_type="bearer"),
        message="注册成功",
    )


@router.post("/login", response_model=ApiResponse[TokenResponse])
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    用户登录：支持使用用户名或注册邮箱登录，校验密码并签发 JWT 访问令牌。
    """
    account = request.username.strip()
    user = db.query(User).filter(
        or_(User.username == account, User.email == account)
    ).first()
    if not user or not verify_password(request.password, user.hashed_password):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response(code=401, message="账号或密码错误").model_dump(),
        )

    access_token = create_access_token(data={"sub": user.username})
    return success_response(
        data=TokenResponse(access_token=access_token, token_type="bearer"),
        message="登录成功",
    )


@router.get("/me", response_model=ApiResponse[UserInfoResponse])
def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    获取当前已登录用户信息。
    """
    return success_response(
        data=UserInfoResponse(
            id=str(current_user.id),
            username=current_user.username,
            email=current_user.email,
            created_at=current_user.created_at,
        ),
        message="获取用户信息成功",
    )
