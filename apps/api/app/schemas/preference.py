"""
用户偏好设置的请求/响应 Schema。
"""
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PreferenceResponse(BaseModel):
    """偏好设置响应"""
    model_config = ConfigDict(from_attributes=True)

    preferred_styles: list[str] = Field(default_factory=list, description="偏好风格列表")
    avoided_colors: list[str] = Field(default_factory=list, description="回避颜色列表")
    custom_weights: dict[str, float] = Field(default_factory=dict, description="自定义推荐权重")


class PreferenceUpdate(BaseModel):
    """偏好设置更新请求（所有字段可选）"""
    preferred_styles: Optional[list[str]] = None
    avoided_colors: Optional[list[str]] = None
    custom_weights: Optional[dict[str, float]] = None
