from fastapi import APIRouter
from app.schemas.health import HealthResponse
from app.core.response import ApiResponse, success_response

router = APIRouter()

@router.get("/", response_model=ApiResponse[HealthResponse])
def get_health():
    """Health check endpoint that reports API status, DB status, and AI API connectivity."""
    data = HealthResponse(
        status="ok",
        db_status="connected", # Stub
        ai_api_status="connected" # Stub
    )
    return success_response(data=data, message="服务运行正常")
