"""
FastAPI 应用入口：初始化中间件、路由与生命周期事件。
"""
import os
import uuid
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.models.user import User


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动时自动建表（开发环境便利，生产环境建议使用 Alembic 迁移）。"""
    # 确保 SQLite 数据库目录存在
    if "sqlite" in settings.DATABASE_URL:
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
            
    # 确保上传目录存在
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs("uploads", exist_ok=True)

    Base.metadata.create_all(bind=engine)
    
    # 自动创建默认用户（暂无用户系统时使用）
    with SessionLocal() as db:
        default_user = db.query(User).filter(User.username == "default_user").first()
        if not default_user:
            default_user = User(
                username="default_user",
                email="default@yijian.ai",
                hashed_password="not-a-real-password",
            )
            db.add(default_user)
            db.commit()
            
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="衣见 AI — 基于多模态视觉与个性化推荐的智能穿搭系统",
    version="0.1.0",
    lifespan=lifespan,
)

# 确保上传目录在模块加载时就存在（StaticFiles 初始化时会检查）
os.makedirs("uploads/clothing", exist_ok=True)

# 挂载静态文件目录用于图片展示
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """为每个请求注入唯一 request_id，支持链路追踪。"""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# 挂载 v1 路由
app.include_router(api_router, prefix=settings.API_V1_STR)
