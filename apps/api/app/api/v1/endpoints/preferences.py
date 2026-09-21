"""
用户偏好设置 API 端点：获取与更新风格偏好、回避色彩与推荐打分权重。
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ApiResponse, success_response
from app.core.security import get_current_user_optional
from app.models.user import User
from app.models.preference import UserPreference
from app.schemas.preference import PreferenceResponse, PreferenceUpdate

router = APIRouter()


@router.get("", response_model=ApiResponse[PreferenceResponse])
@router.get("/", response_model=ApiResponse[PreferenceResponse])
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    """
    获取当前用户的个性化偏好配置。
    若无记录则自动初始化默认配置。
    """
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        pref = UserPreference(
            user_id=current_user.id,
            preferred_styles=[],
            avoided_colors=[],
            custom_weights={},
        )
        db.add(pref)
        db.commit()
        db.refresh(pref)

    return success_response(
        data=PreferenceResponse(
            preferred_styles=pref.preferred_styles or [],
            avoided_colors=pref.avoided_colors or [],
            custom_weights=pref.custom_weights or {},
        ),
        message="获取偏好设置成功",
    )


@router.put("", response_model=ApiResponse[PreferenceResponse])
@router.put("/", response_model=ApiResponse[PreferenceResponse])
def update_preferences(
    update_in: PreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    """
    更新当前用户的个性化偏好配置。
    """
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        pref = UserPreference(
            user_id=current_user.id,
            preferred_styles=[],
            avoided_colors=[],
            custom_weights={},
        )
        db.add(pref)
        db.commit()
        db.refresh(pref)

    if update_in.preferred_styles is not None:
        pref.preferred_styles = update_in.preferred_styles
    if update_in.avoided_colors is not None:
        pref.avoided_colors = update_in.avoided_colors
    if update_in.custom_weights is not None:
        pref.custom_weights = update_in.custom_weights

    db.commit()
    db.refresh(pref)

    return success_response(
        data=PreferenceResponse(
            preferred_styles=pref.preferred_styles or [],
            avoided_colors=pref.avoided_colors or [],
            custom_weights=pref.custom_weights or {},
        ),
        message="更新偏好设置成功",
    )
