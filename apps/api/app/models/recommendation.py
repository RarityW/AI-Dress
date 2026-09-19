import uuid
from datetime import datetime
from typing import Any
from sqlalchemy import String, DateTime, ForeignKey, Float, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class RecommendationRecord(Base):
    __tablename__ = "recommendation_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    city: Mapped[str] = mapped_column(String(50))
    current_temp: Mapped[float] = mapped_column(Float)
    weather_condition: Mapped[str] = mapped_column(String(50))
    scene: Mapped[str] = mapped_column(String(50))
    target_style: Mapped[str] = mapped_column(String(50))
    candidate_outfits: Mapped[list[Any]] = mapped_column(JSON)
    ai_reason: Mapped[str] = mapped_column(String(500), nullable=True)
    feedback_rating: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
