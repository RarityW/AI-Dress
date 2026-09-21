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
    ImageUploadResponse,
    AnalyzeImageRequest,
    VLMAnalysisResponse
)
from app.services.vlm_service import analyze_clothing_image
from app.core.security import get_current_user_optional as get_current_user

router = APIRouter()

SAMPLE_ITEMS = [
    {
        "file_name": "seed_white_tshirt.jpg",
        "category": "top",
        "sub_category": "短袖T恤",
        "primary_color": "白色",
        "secondary_color": "无",
        "style": "casual",
        "thickness": "thin",
        "season": ["summer", "spring", "autumn"],
        "temp_min": 18.0,
        "temp_max": 36.0,
    },
    {
        "file_name": "seed_grey_hoodie.jpg",
        "category": "top",
        "sub_category": "连帽卫衣",
        "primary_color": "灰色",
        "secondary_color": "白色",
        "style": "casual",
        "thickness": "medium",
        "season": ["spring", "autumn", "winter"],
        "temp_min": 10.0,
        "temp_max": 22.0,
    },
    {
        "file_name": "seed_blue_shirt.jpg",
        "category": "top",
        "sub_category": "长袖衬衫",
        "primary_color": "蓝色",
        "secondary_color": "白色",
        "style": "formal",
        "thickness": "medium",
        "season": ["spring", "autumn", "summer"],
        "temp_min": 15.0,
        "temp_max": 27.0,
    },
    {
        "file_name": "seed_black_sweater.jpg",
        "category": "top",
        "sub_category": "针织毛衣",
        "primary_color": "黑色",
        "secondary_color": "无",
        "style": "vintage",
        "thickness": "thick",
        "season": ["autumn", "winter"],
        "temp_min": 2.0,
        "temp_max": 16.0,
    },
    {
        "file_name": "seed_blue_jeans.jpg",
        "category": "bottom",
        "sub_category": "牛仔裤",
        "primary_color": "蓝色",
        "secondary_color": "无",
        "style": "casual",
        "thickness": "medium",
        "season": ["spring", "summer", "autumn", "winter"],
        "temp_min": 8.0,
        "temp_max": 28.0,
    },
    {
        "file_name": "seed_black_trousers.jpg",
        "category": "bottom",
        "sub_category": "西装裤",
        "primary_color": "黑色",
        "secondary_color": "无",
        "style": "formal",
        "thickness": "medium",
        "season": ["spring", "autumn", "winter"],
        "temp_min": 10.0,
        "temp_max": 25.0,
    },
    {
        "file_name": "seed_khaki_chinos.jpg",
        "category": "bottom",
        "sub_category": "休闲裤",
        "primary_color": "卡其色",
        "secondary_color": "无",
        "style": "casual",
        "thickness": "medium",
        "season": ["spring", "summer", "autumn"],
        "temp_min": 12.0,
        "temp_max": 29.0,
    },
    {
        "file_name": "seed_trench_coat.jpg",
        "category": "coat",
        "sub_category": "风衣",
        "primary_color": "卡其色",
        "secondary_color": "黑色",
        "style": "elegant",
        "thickness": "medium",
        "season": ["spring", "autumn"],
        "temp_min": 10.0,
        "temp_max": 20.0,
    },
    {
        "file_name": "seed_black_blazer.jpg",
        "category": "coat",
        "sub_category": "西装外套",
        "primary_color": "黑色",
        "secondary_color": "深灰",
        "style": "formal",
        "thickness": "medium",
        "season": ["spring", "autumn", "winter"],
        "temp_min": 8.0,
        "temp_max": 22.0,
    },
    {
        "file_name": "seed_down_jacket.jpg",
        "category": "coat",
        "sub_category": "羽绒服",
        "primary_color": "黑色",
        "secondary_color": "无",
        "style": "casual",
        "thickness": "thick",
        "season": ["winter"],
        "temp_min": -15.0,
        "temp_max": 8.0,
    },
    {
        "file_name": "seed_white_sneakers.jpg",
        "category": "shoes",
        "sub_category": "板鞋",
        "primary_color": "白色",
        "secondary_color": "灰色",
        "style": "casual",
        "thickness": "medium",
        "season": ["spring", "summer", "autumn", "winter"],
        "temp_min": 5.0,
        "temp_max": 35.0,
    },
    {
        "file_name": "seed_leather_shoes.jpg",
        "category": "shoes",
        "sub_category": "皮鞋",
        "primary_color": "黑色",
        "secondary_color": "棕色",
        "style": "formal",
        "thickness": "medium",
        "season": ["spring", "summer", "autumn", "winter"],
        "temp_min": 5.0,
        "temp_max": 32.0,
    },
    {
        "file_name": "seed_sports_shoes.jpg",
        "category": "shoes",
        "sub_category": "运动鞋",
        "primary_color": "红色",
        "secondary_color": "灰色",
        "style": "sporty",
        "thickness": "medium",
        "season": ["spring", "summer", "autumn", "winter"],
        "temp_min": 8.0,
        "temp_max": 35.0,
    },
    {
        "file_name": "seed_boots.jpg",
        "category": "shoes",
        "sub_category": "靴子",
        "primary_color": "棕色",
        "secondary_color": "黑色",
        "style": "vintage",
        "thickness": "thick",
        "season": ["autumn", "winter"],
        "temp_min": -5.0,
        "temp_max": 18.0,
    },
]


@router.post("/import-samples", response_model=ApiResponse[dict])
def import_sample_wardrobe(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    为当前登录用户一键注入 14 件经典四季测试单品（胶囊衣橱）。
    方便新注册用户开箱即用体验完整的智能穿搭推荐。
    """
    created_count = 0
    for item_def in SAMPLE_ITEMS:
        image_url = f"/uploads/clothing/{item_def['file_name']}"
        clothing = ClothingItem(
            user_id=current_user.id,
            category=item_def["category"],
            sub_category=item_def["sub_category"],
            primary_color=item_def["primary_color"],
            secondary_color=item_def["secondary_color"],
            style=item_def["style"],
            thickness=item_def["thickness"],
            season=item_def["season"],
            temp_min=item_def["temp_min"],
            temp_max=item_def["temp_max"],
            image_url=image_url,
            raw_vlm_attributes={
                "source": "sample_seed_capsule",
                "recommended_for": "course_demo",
            },
        )
        db.add(clothing)
        created_count += 1

    db.commit()
    return success_response(
        data={"count": created_count},
        message=f"已成功为您的专属衣橱导入 {created_count} 件精选四季单品！",
    )

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


@router.post("/analyze", response_model=ApiResponse[VLMAnalysisResponse])
async def analyze_clothing(
    request: AnalyzeImageRequest,
    current_user: User = Depends(get_current_user)
):
    """
    使用多模态视觉大模型智能分析已上传的衣物图片，
    自动提取结构化服装属性（品类、款式、色彩、风格、厚度与适温）。
    """
    result = await analyze_clothing_image(request.image_url)
    return success_response(
        data=VLMAnalysisResponse.model_validate(result),
        message="AI 智能特征提取完成"
    )


@router.post("", response_model=ApiResponse[ClothingItemResponse])
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


@router.get("", response_model=ApiResponse[ClothingListResponse])
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
