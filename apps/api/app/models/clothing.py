import uuid
from datetime import datetime
from typing import Any
from sqlalchemy import String, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class ClothingItem(Base):
    __tablename__ = "clothing_items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    image_url: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(50))
    sub_category: Mapped[str] = mapped_column(String(50))
    primary_color: Mapped[str] = mapped_column(String(50))
    secondary_color: Mapped[str] = mapped_column(String(50), nullable=True)
    style: Mapped[str] = mapped_column(String(50))
    thickness: Mapped[str] = mapped_column(String(50))
    season: Mapped[dict[str, Any]] = mapped_column(JSON)
    temp_min: Mapped[float] = mapped_column(Float)
    temp_max: Mapped[float] = mapped_column(Float)
    raw_vlm_attributes: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
