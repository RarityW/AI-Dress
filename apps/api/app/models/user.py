import uuid
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    account: Mapped[str] = mapped_column(String(50), unique=True, index=True)  # 登录账号（与密码直接关联用于鉴权）
    username: Mapped[str] = mapped_column(String(50), default="新用户")         # 用户名/显示昵称（仅用于页面显示，不用于登录）
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
