from fastapi import APIRouter
from app.core.response import ApiResponse, success_response
from app.schemas.recommendation import RecommendationResponse, OutfitRecommendation

router = APIRouter()

@router.post("/", response_model=ApiResponse[RecommendationResponse])
def get_recommendations():
    """Stub endpoint for recommendations."""
    data = RecommendationResponse(recommendations=[
        OutfitRecommendation(outfit_id="stub", score=0.9, reason="匹配")
    ])
    return success_response(data=data, message="推荐成功")
