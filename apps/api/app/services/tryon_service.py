"""
AI 虚拟试穿服务 (Virtual Try-On Service)。

方案2：双图输入图像级虚拟试穿。
  - 输入1：高质量官方专业模特底图（站姿正面全身）
  - 输入2：用户衣橱真实单品（通过百炼官方通道自动上传至临时 OSS 进行解析）
  - 模型：阿里云百炼官方 OutfitAnyone 虚拟试穿模型 (aitryon)
  - 特性：
    1. 人脸完全保真：保持真实模特五官特征与发型光影，彻底告别畸变
    2. 面料智能贴合：精准解析服装纹理、褶皱、剪裁并迁移至模特身姿
    3. 全自动本地图片上云：通过 DashScope getPolicy 临时通道无缝上传本地图片，无需公网 IP
"""
import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── API 端点 ────────────────────────────────────────────────────────────────
DASHSCOPE_SYNTHESIS_URL = (
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis"
)
DASHSCOPE_UPLOADS_URL = "https://dashscope.aliyuncs.com/api/v1/uploads"
DASHSCOPE_TASK_URL = "https://dashscope.aliyuncs.com/api/v1/tasks"


# ── 官方预设模特图库 ────────────────────────────────────────────────────────
# 使用阿里云 OutfitAnyone 官方认证的标准全身正面模特照
PRESET_MODELS = [
    {
        "id": "female_1",
        "label": "雅琪 (女模)",
        "gender": "female",
        "thumbnail": "/uploads/models/official_model_6.jpg",
        "local_file": "uploads/models/official_model_6.jpg",
        "fallback_url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250626/ubznva/model_person.png",
    },
    {
        "id": "female_2",
        "label": "柔依 (女模)",
        "gender": "female",
        "thumbnail": "/uploads/models/official_model_1.jpg",
        "local_file": "uploads/models/official_model_1.jpg",
        "fallback_url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250626/ubznva/model_person.png",
    },
    {
        "id": "male_1",
        "label": "小轩 (男模)",
        "gender": "male",
        "thumbnail": "/uploads/models/official_model_16.jpg",
        "local_file": "uploads/models/official_model_16.jpg",
        "fallback_url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250626/ubznva/model_person.png",
    },
    {
        "id": "male_2",
        "label": "易峰 (男模)",
        "gender": "male",
        "thumbnail": "/uploads/models/official_model_14.jpg",
        "local_file": "uploads/models/official_model_14.jpg",
        "fallback_url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250626/ubznva/model_person.png",
    },
]

# 内存级 OSS URL 缓存 (避免同张图片重复上传, key: local_path, val: oss://...)
_OSS_CACHE: dict[str, str] = {}


def get_preset_models() -> list[dict[str, str]]:
    """返回预设模特图列表供前端选择。"""
    return [
        {
            "id": m["id"],
            "label": m["label"],
            "gender": m["gender"],
            "thumbnail": m["thumbnail"],
            "full_url": m["thumbnail"],
        }
        for m in PRESET_MODELS
    ]


def _get_model_config(model_id: str) -> dict[str, str]:
    """根据 ID 获取模特配置。"""
    for m in PRESET_MODELS:
        if m["id"] == model_id:
            return m
    return PRESET_MODELS[0]


async def upload_file_to_dashscope_oss(
    file_path: Path,
    api_key: str,
    model_name: str = "aitryon"
) -> Optional[str]:
    """
    通过 DashScope 官方 getPolicy 租约接口，将本地图片文件直传至阿里云内部临时 OSS。
    返回形如 'oss://...' 的地址，可在调用 aitryon 模型时直接传参。
    """
    path_key = str(file_path.resolve())
    if path_key in _OSS_CACHE:
        return _OSS_CACHE[path_key]

    if not file_path.exists():
        logger.error(f"本地图片不存在: {file_path}")
        return None

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. 获取临时上传策略
            policy_resp = await client.get(
                DASHSCOPE_UPLOADS_URL,
                headers={"Authorization": f"Bearer {api_key}"},
                params={"action": "getPolicy", "model": model_name}
            )
            if policy_resp.status_code != 200:
                logger.error(f"获取 DashScope 上传策略失败: {policy_resp.text}")
                return None

            policy_data = policy_resp.json().get("data", {})
            upload_dir = policy_data.get("upload_dir")
            upload_host = policy_data.get("upload_host")
            if not upload_dir or not upload_host:
                logger.error(f"无效的上传策略响应: {policy_resp.text}")
                return None

            key = f"{upload_dir}/{file_path.name}"
            content_type = "image/png" if file_path.suffix.lower() == ".png" else "image/jpeg"

            # 2. 直传临时 OSS
            with open(file_path, "rb") as f:
                file_bytes = f.read()

            files = {
                "OSSAccessKeyId": (None, policy_data["oss_access_key_id"]),
                "Signature": (None, policy_data["signature"]),
                "policy": (None, policy_data["policy"]),
                "x-oss-object-acl": (None, policy_data["x_oss_object_acl"]),
                "x-oss-forbid-overwrite": (None, policy_data["x_oss_forbid_overwrite"]),
                "key": (None, key),
                "success_action_status": (None, "200"),
                "file": (file_path.name, file_bytes, content_type)
            }

            oss_resp = await client.post(upload_host, files=files)
            if oss_resp.status_code in (200, 204):
                oss_url = f"oss://{key}"
                _OSS_CACHE[path_key] = oss_url
                logger.info(f"图片成功上传至 DashScope 临时 OSS: {file_path.name} -> {oss_url}")
                return oss_url
            else:
                logger.error(f"OSS 直传失败 HTTP {oss_resp.status_code}: {oss_resp.text}")
                return None

    except Exception as e:
        logger.error(f"上传图片至 DashScope OSS 异常: {e}")
        return None


async def _resolve_image_to_dashscope_url(
    img_url_or_path: str,
    api_key: str
) -> Optional[str]:
    """
    将图片（可以是公网 URL，也可以是本地路径如 /uploads/...）转换为 DashScope 可解析的地址。
    - 若为公网 http/https URL：直接返回
    - 若为本地相对路径：调用 upload_file_to_dashscope_oss 转换为 oss:// 链接
    """
    if not img_url_or_path:
        return None

    # 如果已经是完整的远程公开图片，直接使用
    if img_url_or_path.startswith("http://") or img_url_or_path.startswith("https://"):
        if "127.0.0.1" not in img_url_or_path and "localhost" not in img_url_or_path:
            return img_url_or_path

    # 本地文件路径解析
    clean_path = img_url_or_path
    if clean_path.startswith("http://127.0.0.1:8000/"):
        clean_path = clean_path.replace("http://127.0.0.1:8000/", "")
    elif clean_path.startswith("/"):
        clean_path = clean_path.lstrip("/")

    local_file = Path(clean_path)
    if not local_file.exists():
        # 尝试相对于应用根目录定位
        alt_path = Path("apps/api") / clean_path
        if alt_path.exists():
            local_file = alt_path

    if local_file.exists():
        return await upload_file_to_dashscope_oss(local_file, api_key)

    logger.warning(f"未能解析本地图片文件: {img_url_or_path}")
    return None


async def generate_virtual_tryon(
    outfit_id: str,
    items: list[dict[str, Any]],
    model_id: str = "female_1",
    scene: str = "daily",
    target_style: str = "casual",
) -> dict[str, Any]:
    """
    调用阿里云百炼 OutfitAnyone (aitryon) 图像级虚拟试穿大模型。

    流程：
    1. 获取模特底图（本地模特直传 OSS 或官方标准图）
    2. 将搭配中的上衣与下装本地图片自动上传至 DashScope 临时 OSS
    3. 调用 aitryon 模型生成高精试衣效果
    4. 轮询并下载最终效果图持久化至本地 uploads/tryon/
    """
    save_dir = Path("uploads") / "tryon"
    save_dir.mkdir(parents=True, exist_ok=True)

    local_filename = f"{outfit_id}_{model_id}.jpg"
    local_filepath = save_dir / local_filename
    local_url = f"/uploads/tryon/{local_filename}"

    # 本地缓存复用
    if local_filepath.exists() and local_filepath.stat().st_size > 5000:
        logger.info(f"命中试穿缓存: {local_url}")
        return {
            "outfit_id": outfit_id,
            "image_url": local_url,
            "model_id": model_id,
            "source": "aitryon",
        }

    api_key = settings.AI_API_KEY
    if not api_key:
        return _error_result(outfit_id, model_id, "未配置 AI_API_KEY，请检查环境变量配置")

    # 1. 准备模特图
    model_cfg = _get_model_config(model_id)
    local_model_path = Path(model_cfg["local_file"])
    person_image_url = None

    if local_model_path.exists():
        person_image_url = await upload_file_to_dashscope_oss(local_model_path, api_key)

    if not person_image_url:
        person_image_url = model_cfg.get("fallback_url")

    # 2. 提取上装与下装并上传至 DashScope OSS
    top_garment_url: Optional[str] = None
    bottom_garment_url: Optional[str] = None

    for item in items:
        cat = item.get("category", "")
        img = item.get("image_url", "")
        if not img:
            continue

        if cat in ("top", "coat") and not top_garment_url:
            top_garment_url = await _resolve_image_to_dashscope_url(img, api_key)
        elif cat == "bottom" and not bottom_garment_url:
            bottom_garment_url = await _resolve_image_to_dashscope_url(img, api_key)

    # 必须至少有一件衣物
    if not top_garment_url and not bottom_garment_url:
        return _error_result(outfit_id, model_id, "搭配方案中无可识别的衣物图片，无法发起试穿")

    logger.info(
        f"发起 OutfitAnyone 试穿: outfit={outfit_id}, model={model_id}, "
        f"person={person_image_url[:40]}..., top={'有' if top_garment_url else '无'}, bottom={'有' if bottom_garment_url else '无'}"
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
        "X-DashScope-OssResourceResolve": "enable",
    }

    input_payload: dict[str, Any] = {
        "person_image_url": person_image_url,
    }
    if top_garment_url:
        input_payload["top_garment_url"] = top_garment_url
    if bottom_garment_url:
        input_payload["bottom_garment_url"] = bottom_garment_url

    payload = {
        "model": "aitryon",
        "input": input_payload,
        "parameters": {
            "resolution": -1,
            "restore_face": True,
        }
    }

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            submit_resp = await client.post(
                DASHSCOPE_SYNTHESIS_URL,
                headers=headers,
                json=payload,
            )

            if submit_resp.status_code != 200:
                err_text = submit_resp.text
                logger.error(f"aitryon 任务提交失败 HTTP {submit_resp.status_code}: {err_text}")
                return _error_result(
                    outfit_id, model_id,
                    f"试穿任务提交失败: {err_text[:120]}"
                )

            task_id = submit_resp.json().get("output", {}).get("task_id")
            if not task_id:
                return _error_result(outfit_id, model_id, f"未能获取试穿 task_id: {submit_resp.text[:120]}")

            logger.info(f"aitryon 试衣任务已提交成功: task_id={task_id}")

            # 轮询任务状态（aitryon 通常 5~15 秒完成，每 2.5 秒查询一次，最多等 50 秒）
            poll_headers = {"Authorization": f"Bearer {api_key}"}
            generated_img_url: Optional[str] = None

            for i in range(20):
                await asyncio.sleep(2.5)
                poll_resp = await client.get(
                    f"{DASHSCOPE_TASK_URL}/{task_id}",
                    headers=poll_headers,
                    timeout=10.0
                )
                if poll_resp.status_code != 200:
                    continue

                poll_data = poll_resp.json()
                task_status = poll_data.get("output", {}).get("task_status")

                if task_status == "SUCCEEDED":
                    generated_img_url = poll_data.get("output", {}).get("image_url")
                    break
                elif task_status in ("FAILED", "CANCELED"):
                    err_msg = poll_data.get("output", {}).get("message", "生成任务失败")
                    logger.error(f"aitryon 任务失败: {err_msg}")
                    return _error_result(outfit_id, model_id, f"试衣生成失败: {err_msg}")

            if generated_img_url:
                # 下载结果图片并持久化至本地
                dl_resp = await client.get(generated_img_url, timeout=30.0)
                if dl_resp.status_code == 200:
                    local_filepath.write_bytes(dl_resp.content)
                    logger.info(f"虚拟试穿效果图已保存至: {local_url}")
                    return {
                        "outfit_id": outfit_id,
                        "image_url": local_url,
                        "model_id": model_id,
                        "source": "aitryon",
                    }
                else:
                    return _error_result(outfit_id, model_id, f"结果图拉取失败 (HTTP {dl_resp.status_code})")

    except httpx.TimeoutException:
        return _error_result(outfit_id, model_id, "请求超时，请检查网络或稍后重试")
    except Exception as e:
        logger.error(f"虚拟试穿执行异常: {e}", exc_info=True)
        return _error_result(outfit_id, model_id, f"虚拟试穿服务异常: {str(e)}")

    return _error_result(outfit_id, model_id, "试穿生成超时（已超 50 秒），请稍后重试")


def _error_result(outfit_id: str, model_id: str, error: str) -> dict[str, Any]:
    """统一错误返回。"""
    return {
        "outfit_id": outfit_id,
        "image_url": "",
        "model_id": model_id,
        "source": "error",
        "error": error,
    }


# ── 向后兼容包装 ────────────────────────────────────────────────────────────
async def generate_tryon_image(
    outfit_id: str,
    items: list[dict[str, Any]],
    gender: str = "unisex",
    scene: str = "daily",
    target_style: str = "casual",
    model_id: str = "female_1",
) -> dict[str, Any]:
    """向后兼容接口。"""
    if gender == "male" and model_id == "female_1":
        model_id = "male_1"

    result = await generate_virtual_tryon(
        outfit_id=outfit_id,
        items=items,
        model_id=model_id,
        scene=scene,
        target_style=target_style,
    )
    result.setdefault("prompt", "aitryon outfitanyone")
    return result
