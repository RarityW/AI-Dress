"""预设模特图 API 端点。"""
from fastapi import APIRouter

from app.core.response import success_response, ApiResponse
from app.services.tryon_service import get_preset_models

router = APIRouter()


@router.get("", response_model=ApiResponse[list[dict]])
@router.get("/", response_model=ApiResponse[list[dict]])
def list_preset_models():
    """
    获取虚拟试穿可用的预设模特列表。
    每个模特包含：id, label, gender, thumbnail, full_url
    """
    models = get_preset_models()
    return success_response(data=models, message="获取预设模特列表成功")
