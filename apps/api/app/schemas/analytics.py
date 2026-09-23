from typing import Optional
from pydantic import BaseModel, ConfigDict


class MetricOverview(BaseModel):
    total_items: int
    total_outfits: int
    utilization_rate: float
    capsule_score: int
    capsule_level: str


class DistributionItem(BaseModel):
    key: str
    label: str
    count: int
    percentage: float
    color: Optional[str] = None


class ColorDistributionItem(BaseModel):
    color_name: str
    hex_code: str
    count: int
    percentage: float
    is_neutral: bool


class VersatileItem(BaseModel):
    id: str
    category: str
    sub_category: str
    primary_color: str
    style: str
    image_url: str
    match_count: int
    versatility_score: float
    highlight_reason: str


class IdleItem(BaseModel):
    id: str
    category: str
    sub_category: str
    primary_color: str
    style: str
    image_url: str
    temp_range: str
    idle_days: int
    revive_suggestion: str


class WardrobeDiagnosis(BaseModel):
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    purchase_suggestions: list[str]


class AnalyticsOverviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    metrics: MetricOverview
    categories: list[DistributionItem]
    seasons: list[DistributionItem]
    styles: list[DistributionItem]
    colors: list[ColorDistributionItem]
    neutral_ratio: float
    versatile_items: list[VersatileItem]
    idle_items: list[IdleItem]
    diagnosis: WardrobeDiagnosis
