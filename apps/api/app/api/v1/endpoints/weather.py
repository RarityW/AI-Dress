from fastapi import APIRouter, Query
from app.core.response import ApiResponse, success_response
from app.schemas.weather import WeatherResponse
from app.services.weather_service import get_realtime_weather

router = APIRouter()

@router.get("", response_model=ApiResponse[WeatherResponse])
@router.get("/", response_model=ApiResponse[WeatherResponse])
async def get_weather(city: str = Query(default="北京", description="城市名称")):
    """获取指定城市的实时气象数据（支持 Open-Meteo 实时、心知天气与离线智能保底）。"""
    weather_data = await get_realtime_weather(city)
    data = WeatherResponse(**weather_data)
    return success_response(data=data, message=f"{city}实时天气获取成功")

