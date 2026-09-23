"""
衣橱数据洞察 API 端点：资产分布、色彩谱系、百搭王与闲置预警。
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ApiResponse, success_response
from app.core.security import get_current_user_optional
from app.models.user import User
from app.models.clothing import ClothingItem
from app.models.outfit import Outfit
from app.schemas.analytics import AnalyticsOverviewResponse
from app.services.analytics_service import analyze_wardrobe_overview

router = APIRouter()


@router.get("", response_model=ApiResponse[AnalyticsOverviewResponse])
@router.get("/", response_model=ApiResponse[AnalyticsOverviewResponse])
@router.get("/overview", response_model=ApiResponse[AnalyticsOverviewResponse])
@router.get("/overview/", response_model=ApiResponse[AnalyticsOverviewResponse])
def get_wardrobe_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    """
    获取当前用户的衣橱全景数据分析与诊断。
    包含资产指标、品类/色彩/季节分布、百搭单品榜、闲置预警及胶囊健康度。
    """
    items = db.query(ClothingItem).filter(ClothingItem.user_id == current_user.id).all()
    outfits = db.query(Outfit).filter(Outfit.user_id == current_user.id).all()

    analysis_result = analyze_wardrobe_overview(items=items, outfits=outfits)

    return success_response(
        data=analysis_result,
        message="获取衣橱数据洞察成功",
    )
