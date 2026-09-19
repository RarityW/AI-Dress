from fastapi import APIRouter
from app.core.response import ApiResponse, success_response
from app.schemas.clothing import ClothingItemResponse

router = APIRouter()

@router.get("/", response_model=ApiResponse[list[ClothingItemResponse]])
def get_clothes():
    """Stub endpoint for fetching clothing."""
    return success_response(data=[], message="获取成功")
