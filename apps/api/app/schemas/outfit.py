"""
搭配收藏的请求/响应 Schema。
"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class OutfitCreate(BaseModel):
    """收藏一套搭配"""
    name: str = Field(..., min_length=1, max_length=100, description="搭配名称")
    occasion: str = Field(default="", description="场景")
    season: str = Field(default="", description="季节")
    item_ids: list[str] = Field(..., description="衣物 ID 列表")
    overall_score: Optional[float] = Field(None, description="推荐评分")


class OutfitItemBrief(BaseModel):
    """搭配中单件衣物的摘要"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    image_url: Optional[str] = None
    category: Optional[str] = None
    primary_color: Optional[str] = None
    style: Optional[str] = None


class OutfitResponse(BaseModel):
    """搭配收藏响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    occasion: str
    season: str
    item_ids: list[Any] = Field(default_factory=list)
    items: list[OutfitItemBrief] = Field(default_factory=list, description="衣物详情列表")
    overall_score: Optional[float] = None
    created_at: Optional[datetime] = None


class OutfitListResponse(BaseModel):
    """搭配列表响应"""
    items: list[OutfitResponse]
    total: int
