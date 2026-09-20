import os
import uuid
from typing import Any
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import cast, String

from app.core.config import settings
from app.core.database import get_db
from app.core.response import ApiResponse, success_response, error_response
from app.models.user import User
from app.models.clothing import ClothingItem
from app.schemas.clothing import (
    ClothingItemCreate,
    ClothingItemUpdate,
    ClothingItemResponse,
    ClothingListResponse,
    ImageUploadResponse
)

router = APIRouter()

def get_current_user(db: Session = Depends(get_db)) -> User:
    """获取当前用户（暂无登录系统，使用默认用户）。"""
    user = db.query(User).filter(User.username == "default_user").first()
    if not user:
        user = User(
            username="default_user",
            email="default@yijian.ai",
            hashed_password="not-a-real-password",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.post("/upload-image", response_model=ApiResponse[ImageUploadResponse])
async def upload_image(file: UploadFile = File(...)):
    """上传衣物图片"""
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        return JSONResponse(
            status_code=400,
            content=error_response(code=400, message="不支持的图片类型").model_dump()
        )
    
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        return JSONResponse(
            status_code=413,
            content=error_response(code=413, message=f"图片大小不能超过 {settings.MAX_UPLOAD_SIZE_MB}MB").model_dump()
        )
        
    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
        
    image_url = f"/{settings.UPLOAD_DIR}/{filename}".replace("\\", "/")
    
    return success_response(data=ImageUploadResponse(image_url=image_url, filename=filename))


@router.post("/", response_model=ApiResponse[ClothingItemResponse])
def create_clothing(
    item_in: ClothingItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建衣物"""
    db_item = ClothingItem(
        user_id=current_user.id,
        category=item_in.category,
        sub_category=item_in.sub_category,
        primary_color=item_in.primary_color,
        secondary_color=item_in.secondary_color,
        style=item_in.style,
        thickness=item_in.thickness,
        season=item_in.season,
        temp_min=item_in.temp_min,
        temp_max=item_in.temp_max,
        image_url=item_in.image_url,
        raw_vlm_attributes=item_in.raw_vlm_attributes
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return success_response(data=ClothingItemResponse.model_validate(db_item))


@router.get("/", response_model=ApiResponse[ClothingListResponse])
def list_clothing(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str = None,
    style: str = None,
    season: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取衣物列表"""
    query = db.query(ClothingItem).filter(ClothingItem.user_id == current_user.id)
    
    if category:
        query = query.filter(ClothingItem.category == category)
    if style:
        query = query.filter(ClothingItem.style == style)
    if season:
        query = query.filter(cast(ClothingItem.season, String).like(f'%"{season}"%'))
        
    total = query.count()
    items = query.order_by(ClothingItem.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return success_response(data=ClothingListResponse(
        items=[ClothingItemResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    ))

@router.get("/{item_id}", response_model=ApiResponse[ClothingItemResponse])
def get_clothing(
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单件衣物详情"""
    item = db.query(ClothingItem).filter(
        ClothingItem.id == item_id,
        ClothingItem.user_id == current_user.id
    ).first()
    
    if not item:
        return JSONResponse(
            status_code=404,
            content=error_response(code=404, message="衣物不存在").model_dump()
        )
        
    return success_response(data=ClothingItemResponse.model_validate(item))

@router.put("/{item_id}", response_model=ApiResponse[ClothingItemResponse])
def update_clothing(
    item_id: uuid.UUID,
    item_in: ClothingItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新衣物信息"""
    item = db.query(ClothingItem).filter(
        ClothingItem.id == item_id,
        ClothingItem.user_id == current_user.id
    ).first()
    
    if not item:
        return JSONResponse(
            status_code=404,
            content=error_response(code=404, message="衣物不存在").model_dump()
        )
        
    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
        
    db.commit()
    db.refresh(item)
    
    return success_response(data=ClothingItemResponse.model_validate(item))

@router.delete("/{item_id}", response_model=ApiResponse[Any])
def delete_clothing(
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除衣物"""
    item = db.query(ClothingItem).filter(
        ClothingItem.id == item_id,
        ClothingItem.user_id == current_user.id
    ).first()
    
    if not item:
        return JSONResponse(
            status_code=404,
            content=error_response(code=404, message="衣物不存在").model_dump()
        )
        
    if item.image_url:
        file_path = item.image_url.lstrip("/")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
                
    db.delete(item)
    db.commit()
    
    return success_response(message="删除成功")
