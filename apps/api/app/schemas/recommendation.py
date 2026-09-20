"""穿搭推荐相关 Pydantic 数据契约。"""
import uuid
from typing import Optional, Any
from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """穿搭推荐请求参数。"""
    city: str = Field(default="北京", description="城市名称")
    temperature: Optional[float] = Field(default=20.0, description="当前温度(℃)，若未提供则使用默认或气象预估")
    weather_condition: Optional[str] = Field(default="晴", description="天气状况(晴/多云/阴/小雨等)")
    scene: str = Field(default="daily", description="场景: daily(日常), work(工作通勤), date(约会), sports(运动), class(上课), party(聚会)")
    target_style: str = Field(default="casual", description="偏好风格: casual(休闲), formal(正式), sporty(运动), minimal(简约), vintage(复古), street(街头)")
    top_k: int = Field(default=3, ge=1, le=10, description="返回最优方案套数")


class OutfitItemDetail(BaseModel):
    """搭配中单件衣物的详细信息。"""
    id: str
    category: str
    sub_category: str
    primary_color: str
    secondary_color: Optional[str] = None
    style: str
    thickness: str
    image_url: str
    temp_min: float
    temp_max: float


class ScoreBreakdown(BaseModel):
    """评分各维度拆解详情。"""
    weather_score: float = Field(..., description="气象契合度 (0~100)")
    style_score: float = Field(..., description="风格契合度 (0~100)")
    scene_score: float = Field(..., description="场景契合度 (0~100)")
    color_score: float = Field(..., description="色彩协调度 (0~100)")
    overall_score: float = Field(..., description="综合匹配度得分 (0~100)")


class OutfitRecommendation(BaseModel):
    """一套穿搭搭配方案推荐结果。"""
    outfit_id: str
    items: list[OutfitItemDetail]
    scores: ScoreBreakdown
    reason: str


class RecommendationResponse(BaseModel):
    """推荐结果整体响应。"""
    record_id: Optional[str] = None
    city: str
    current_temp: float
    weather_condition: str
    scene: str
    target_style: str
    total_candidates: int
    recommendations: list[OutfitRecommendation]


class FeedbackRequest(BaseModel):
    """用户对推荐结果的满意度评价。"""
    rating: int = Field(..., ge=1, le=5, description="评分: 1~5 星")


class TryOnRequest(BaseModel):
    """AI 试穿生图请求契约。"""
    outfit_id: str = Field(..., description="方案 UUID")
    items: list[dict[str, Any]] = Field(..., description="方案所含单品简要列表")
    gender: str = Field(default="unisex", description="模特性别: female, male, unisex")
    scene: str = Field(default="daily", description="搭配场景")
    target_style: str = Field(default="casual", description="风格基调")


class TryOnResponse(BaseModel):
    """AI 试穿生图结果响应。"""
    outfit_id: str
    image_url: str
    prompt: str
    source: str

