"""
搭配收藏 API 端点：收藏搭配、查看收藏列表、删除收藏搭配。
"""
import uuid
from typing import Any
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ApiResponse, success_response, error_response
from app.core.security import get_current_user_optional
from app.models.user import User
from app.models.clothing import ClothingItem
from app.models.outfit import Outfit
from app.schemas.outfit import (
    OutfitCreate,
    OutfitResponse,
    OutfitListResponse,
    OutfitItemBrief,
)

router = APIRouter()


def _populate_outfit_response(outfit: Outfit, db: Session) -> OutfitResponse:
    """辅助函数：根据 outfit.item_ids 组装搭配中的单品简要信息"""
    item_ids_raw = outfit.item_ids or []
    item_id_uuids = []
    for i in item_ids_raw:
        try:
            item_id_uuids.append(uuid.UUID(str(i)))
        except (ValueError, AttributeError):
            pass

    items = []
    if item_id_uuids:
        clothing_items = db.query(ClothingItem).filter(ClothingItem.id.in_(item_id_uuids)).all()
        # 保持 item_ids 中的顺序
        item_map = {str(item.id): item for item in clothing_items}
        for i in item_ids_raw:
            str_id = str(i)
            if str_id in item_map:
                c = item_map[str_id]
                items.append(
                    OutfitItemBrief(
                        id=str(c.id),
                        image_url=c.image_url,
                        category=c.category,
                        primary_color=c.primary_color,
                        style=c.style,
                    )
                )

    return OutfitResponse(
        id=str(outfit.id),
        name=outfit.name,
        occasion=outfit.occasion or "",
        season=outfit.season or "",
        item_ids=[str(i) for i in item_ids_raw],
        items=items,
        overall_score=outfit.overall_score,
        created_at=outfit.created_at,
    )


@router.post("", response_model=ApiResponse[OutfitResponse])
@router.post("/", response_model=ApiResponse[OutfitResponse])
def create_outfit(
    outfit_in: OutfitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    """
    保存一套搭配到「我的收藏」。
    """
    db_outfit = Outfit(
        user_id=current_user.id,
        name=outfit_in.name,
        occasion=outfit_in.occasion,
        season=outfit_in.season,
        item_ids=outfit_in.item_ids,
        overall_score=outfit_in.overall_score,
    )
    db.add(db_outfit)
    db.commit()
    db.refresh(db_outfit)

    res_data = _populate_outfit_response(db_outfit, db)
    return success_response(data=res_data, message="搭配收藏成功")


@router.get("", response_model=ApiResponse[OutfitListResponse])
@router.get("/", response_model=ApiResponse[OutfitListResponse])
def list_outfits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    """
    获取当前用户的所有收藏搭配列表。
    """
    outfits = (
        db.query(Outfit)
        .filter(Outfit.user_id == current_user.id)
        .order_by(Outfit.created_at.desc())
        .all()
    )

    items = [_populate_outfit_response(o, db) for o in outfits]
    return success_response(
        data=OutfitListResponse(items=items, total=len(items)),
        message="获取收藏搭配成功",
    )


@router.delete("/{outfit_id}", response_model=ApiResponse[Any])
def delete_outfit(
    outfit_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    """
    从收藏中移除指定搭配。
    """
    outfit = (
        db.query(Outfit)
        .filter(Outfit.id == outfit_id, Outfit.user_id == current_user.id)
        .first()
    )
    if not outfit:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(code=404, message="搭配记录不存在").model_dump(),
        )

    db.delete(outfit)
    db.commit()
    return success_response(message="取消收藏成功")
