"""穿搭推荐 API 端点。"""
import uuid
from typing import Optional, Any
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ApiResponse, success_response, error_response
from app.api.v1.endpoints.clothing import get_current_user
from app.models.user import User
from app.models.clothing import ClothingItem
from app.models.recommendation import RecommendationRecord
from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    FeedbackRequest
)
from app.services.recommendation.engine import recommend_outfits

router = APIRouter()


@router.post("/", response_model=ApiResponse[RecommendationResponse])
def create_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    智能穿搭推荐主接口：
    基于用户数字衣橱中的所有衣物单品，结合气温、场景、风格等需求，
    由自研多维度推荐引擎输出 TOP-K 搭配组合与推荐理由。
    """
    # 1. 提取当前用户所有衣橱单品
    user_items = db.query(ClothingItem).filter(ClothingItem.user_id == current_user.id).all()

    # 2. 执行自主推荐算法
    recommendations = recommend_outfits(user_items, request)

    # 3. 持久化本次推荐记录到数据库
    record_id = None
    try:
        candidate_dump = [r.model_dump() for r in recommendations]
        primary_reason = recommendations[0].reason if recommendations else "衣橱暂无符合该场景的合适搭配"

        rec_record = RecommendationRecord(
            user_id=current_user.id,
            city=request.city,
            current_temp=float(request.temperature or 20.0),
            weather_condition=request.weather_condition or "晴",
            scene=request.scene,
            target_style=request.target_style,
            candidate_outfits=candidate_dump,
            ai_reason=primary_reason
        )
        db.add(rec_record)
        db.commit()
        db.refresh(rec_record)
        record_id = str(rec_record.id)
    except Exception:
        db.rollback()

    response_data = RecommendationResponse(
        record_id=record_id,
        city=request.city,
        current_temp=float(request.temperature or 20.0),
        weather_condition=request.weather_condition or "晴",
        scene=request.scene,
        target_style=request.target_style,
        total_candidates=len(user_items),
        recommendations=recommendations
    )

    msg = "推荐方案生成成功" if recommendations else "当前衣橱衣物较少，请先在【衣橱】上传更多衣物"
    return success_response(data=response_data, message=msg)


@router.get("/history", response_model=ApiResponse[list[dict[str, Any]]])
def get_recommendation_history(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户最近的历史推荐记录。"""
    records = db.query(RecommendationRecord).filter(
        RecommendationRecord.user_id == current_user.id
    ).order_by(RecommendationRecord.created_at.desc()).limit(limit).all()

    result = []
    for r in records:
        result.append({
            "id": str(r.id),
            "city": r.city,
            "current_temp": r.current_temp,
            "weather_condition": r.weather_condition,
            "scene": r.scene,
            "target_style": r.target_style,
            "candidate_outfits": r.candidate_outfits,
            "ai_reason": r.ai_reason,
            "feedback_rating": r.feedback_rating,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })

    return success_response(data=result, message="获取历史推荐成功")


@router.post("/{record_id}/feedback", response_model=ApiResponse[Any])
def submit_recommendation_feedback(
    record_id: uuid.UUID,
    feedback: FeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """用户对推荐结果提交 1~5 星反馈评价。"""
    record = db.query(RecommendationRecord).filter(
        RecommendationRecord.id == record_id,
        RecommendationRecord.user_id == current_user.id
    ).first()

    if not record:
        return JSONResponse(
            status_code=404,
            content=error_response(code=404, message="推荐记录不存在").model_dump()
        )

    record.feedback_rating = feedback.rating
    db.commit()
    return success_response(message="感谢您的反馈！")
