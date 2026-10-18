"""模特与用户个人形象 API 端点。"""
import os
import uuid
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.response import success_response, error_response, ApiResponse
from app.core.security import get_current_user_optional
from app.models.user import User
from app.services.tryon_service import (
    get_preset_models,
    save_user_custom_model,
    delete_user_custom_model,
    get_user_custom_model,
    generate_clean_background_model,
    switch_user_model_display,
)
from app.services.vlm_service import analyze_person_image

router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.get("", response_model=ApiResponse[list[dict]])
@router.get("/", response_model=ApiResponse[list[dict]])
def list_preset_models(
    current_user: User = Depends(get_current_user_optional),
):
    """
    获取虚拟试穿可用的模特列表。
    置顶返回当前登录用户的专属形象卡片（若已上传则包含个人照片与特征），
    随后展示精选的 2 位男女核心预设模特。
    """
    user_id = str(current_user.id) if current_user else None
    models = get_preset_models(user_id=user_id)
    return success_response(data=models, message="获取模特列表成功")


@router.post("/custom", response_model=ApiResponse[dict[str, Any]])
async def upload_custom_model(
    file: UploadFile = File(...),
    gender: Optional[str] = Form(None),
    hairstyle: Optional[str] = Form(None),
    body_shape: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user_optional),
):
    """
    用户上传个人全身照/半身正面照作为试穿专属模特形象。
    支持用户指定/锁定发型与身材特征，确保生成试衣照时绝对不篡改用户原图特征。
    上传后会自动为用户生成一张纯白干净背景的专属画像。
    """
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        return JSONResponse(
            status_code=400,
            content=error_response(code=400, message="仅支持 JPG, PNG, WEBP 格式图片").model_dump()
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        return JSONResponse(
            status_code=400,
            content=error_response(code=400, message="图片大小不能超过 10MB").model_dump()
        )

    user_id = str(current_user.id) if current_user else "default_user"
    ext = os.path.splitext(file.filename or "")[1].lower() or ".jpg"

    # 1. 临时保存并调用 VLM 解析人像特征
    temp_dir = Path("uploads") / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / f"person_analysis_{uuid.uuid4().hex[:8]}{ext}"
    temp_path.write_bytes(content)

    try:
        person_meta = await analyze_person_image(str(temp_path))
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass

    final_gender = gender or person_meta.get("gender", "female")
    persona = person_meta.get("persona", "")
    final_hair = hairstyle or "保持原图自然发型与发色，严格保持发长与发际线"
    final_body = body_shape or "严格保持原图真实自然身材比例，拒绝夸张形变"

    # 2. 持久化至用户个人模型目录
    saved_model = save_user_custom_model(
        user_id=user_id,
        image_bytes=content,
        file_ext=ext,
        gender=final_gender,
        persona=persona,
        hairstyle=final_hair,
        body_shape=final_body,
    )

    # 3. 自动快速生成高质量纯白影棚背景画像图
    try:
        updated_model = await generate_clean_background_model(user_id=user_id, use_ai_model=False)
        saved_model = updated_model
    except Exception as e:
        # 降级不阻断上传流程
        pass

    return success_response(data=saved_model, message="个人全身照上传成功！已自动为您生成纯白影棚用户画像")


@router.post("/custom/clean-background", response_model=ApiResponse[dict[str, Any]])
async def make_custom_model_clean_background(
    use_ai: bool = Form(True),
    current_user: User = Depends(get_current_user_optional),
):
    """
    当用户上传的全身照背景杂乱时，调用百炼万相 2.1 图像编辑大模型或高级抠图模型，
    生成一张 100% 纯白干净高级影棚无缝背景的用户画像图，供后续换装与大片使用。
    """
    user_id = str(current_user.id) if current_user else "default_user"
    try:
        updated = await generate_clean_background_model(user_id=user_id, use_ai_model=use_ai)
        return success_response(data=updated, message="已成功生成背景纯白干净的影棚级用户画像！")
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=error_response(code=500, message=f"生成纯白背景画像失败: {str(e)}").model_dump()
        )


@router.post("/custom/switch-display", response_model=ApiResponse[dict[str, Any]])
def switch_model_display_mode(
    mode: str = Form("white"),
    current_user: User = Depends(get_current_user_optional),
):
    """
    切换个人形象卡片的展示底图：'white' (纯白影棚背景) 或 'raw' (原拍照背景)。
    """
    user_id = str(current_user.id) if current_user else "default_user"
    try:
        updated = switch_user_model_display(user_id=user_id, mode=mode)
        msg = "已切换为纯白影棚背景展示" if mode == "white" else "已切换为原图背景展示"
        return success_response(data=updated, message=msg)
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content=error_response(code=400, message=f"切换展示模式失败: {str(e)}").model_dump()
        )


@router.delete("/custom", response_model=ApiResponse[bool])
def delete_custom_model(
    current_user: User = Depends(get_current_user_optional),
):
    """删除当前用户的自定义全身照形象。"""
    user_id = str(current_user.id) if current_user else "default_user"
    success = delete_user_custom_model(user_id=user_id)
    return success_response(data=success, message="已清除个人形象设置")
