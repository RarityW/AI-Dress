"""气象服务 Pydantic 数据契约。"""
from typing import Optional
from pydantic import BaseModel, Field


class WeatherResponse(BaseModel):
    """实时气象数据响应。"""
    city: str = Field(..., description="城市名称")
    temperature: float = Field(..., description="实时温度 (℃)")
    condition: str = Field(..., description="气象状况中文 (晴 / 多云 / 阴 / 小雨 等)")
    condition_code: str = Field(default="sunny", description="标准气象代号: sunny, cloudy, overcast, rainy, snowy, foggy")
    humidity: Optional[float] = Field(None, description="相对湿度 (%)")
    wind_speed: Optional[float] = Field(None, description="风速 (km/h)")
    feels_like: Optional[float] = Field(None, description="体感温度 (℃)")
    source: str = Field(default="live", description="数据来源: open-meteo, seniverse, fallback")
