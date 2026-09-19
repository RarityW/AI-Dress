from fastapi import APIRouter
from app.core.response import ApiResponse, success_response
from app.schemas.weather import WeatherResponse

router = APIRouter()

@router.get("/", response_model=ApiResponse[WeatherResponse])
def get_weather(city: str):
    """Stub endpoint for weather."""
    data = WeatherResponse(city=city, temperature=22.0, condition="Sunny")
    return success_response(data=data, message="天气获取成功")
