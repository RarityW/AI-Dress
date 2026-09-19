import uuid
from datetime import datetime
from typing import Any
from sqlalchemy import String, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Outfit(Base):
    __tablename__ = "outfits"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(100))
    occasion: Mapped[str] = mapped_column(String(50))
    season: Mapped[str] = mapped_column(String(50))
    item_ids: Mapped[list[Any]] = mapped_column(JSON)
    overall_score: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
