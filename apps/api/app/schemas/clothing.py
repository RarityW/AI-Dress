"""衣物相关 Pydantic 数据契约。"""
import uuid
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, Field


class ClothingItemBase(BaseModel):
    """衣物基础字段。"""
    category: str = Field(..., description="类别: top, bottom, coat, shoes, accessory")
    sub_category: str = Field(..., description="子类别: hoodie, jeans, sneakers 等")
    primary_color: str = Field(..., description="主色调")
    secondary_color: Optional[str] = Field(None, description="辅助色调")
    style: str = Field(..., description="风格: casual, formal, sporty, minimal 等")
    thickness: str = Field(..., description="厚度: thin, medium, thick")
    season: list[str] = Field(..., description="适用季节列表: spring, summer, autumn, winter")
    temp_min: float = Field(..., description="适宜最低温度 ℃")
    temp_max: float = Field(..., description="适宜最高温度 ℃")


class ClothingItemCreate(ClothingItemBase):
    """创建衣物时的请求体（不含图片，图片通过单独上传接口）。"""
    image_url: Optional[str] = Field(None, description="图片路径，由上传接口返回")
    raw_vlm_attributes: Optional[dict[str, Any]] = Field(None, description="VLM 识别原始 JSON")


class ClothingItemUpdate(BaseModel):
    """更新衣物时的请求体，所有字段可选。"""
    category: Optional[str] = None
    sub_category: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    style: Optional[str] = None
    thickness: Optional[str] = None
    season: Optional[list[str]] = None
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None


class ClothingItemResponse(ClothingItemBase):
    """衣物详情响应。"""
    id: uuid.UUID
    user_id: uuid.UUID
    image_url: str
    raw_vlm_attributes: Optional[dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClothingListResponse(BaseModel):
    """衣物列表响应（含分页信息）。"""
    items: list[ClothingItemResponse]
    total: int
    page: int
    page_size: int


class ImageUploadResponse(BaseModel):
    """图片上传成功的响应。"""
    image_url: str
    filename: str
