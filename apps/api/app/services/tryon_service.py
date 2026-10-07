"""
AI 虚拟试穿与时尚生图服务 (Virtual Try-On & Fashion Generation Service)。

支持双生图引擎：
1. 🌟 通义千问生图旗舰 (Qwen-Image-Plus)：
   - 基于搭配中单品的材质、版型、色彩与穿搭场景，生成超真实自然人像时尚大片。
   - 具有真实皮肤质感、自然微表情、发丝光影和单反景深，彻底告别假面与畸变。
2. 👗 百炼高保真虚拟试衣 (OutfitAnyone aitryon-plus)：
   - 基于用户衣橱真实平铺图片（通过百炼官方通道自动上传至临时 OSS 进行解析）。
   - 1:1 提取服装材质与版型精确贴合至选定的模特身姿。
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
DASHSCOPE_T2I_URL = (
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
)
DASHSCOPE_UPLOADS_URL = "https://dashscope.aliyuncs.com/api/v1/uploads"
DASHSCOPE_TASK_URL = "https://dashscope.aliyuncs.com/api/v1/tasks"


# ── 官方预设模特图库 (8 位男女专业模特) ────────────────────────────────────
PRESET_MODELS = [
    {
        "id": "male_1",
        "label": "小轩 (男模 · 阳光俊朗)",
        "gender": "male",
        "thumbnail": "/uploads/models/official_model_16.jpg",
        "local_file": "uploads/models/official_model_16.jpg",
        "persona": "handsome and confident East Asian young male model in his 20s, clean-shaven, sharp jawline, natural friendly expression",
        "fallback_url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250626/ubznva/model_person.png",
    },
    {
        "id": "female_1",
        "label": "雅琪 (女模 · 优雅知性)",
        "gender": "female",
        "thumbnail": "/uploads/models/official_model_6.jpg",
        "local_file": "uploads/models/official_model_6.jpg",
        "persona": "elegant and graceful East Asian female model in her 20s, sophisticated natural makeup, soft smile, gentle refined features",
        "fallback_url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250626/ubznva/model_person.png",
    },
    {
        "id": "male_2",
        "label": "易峰 (男模 · 商务沉稳)",
        "gender": "male",
        "thumbnail": "/uploads/models/official_model_3.jpg",
        "local_file": "uploads/models/official_model_3.jpg",
        "persona": "mature and poised Asian male model in his late 20s, calm confident gaze, well-groomed hair, refined professional posture",
        "fallback_url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250626/ubznva/model_person.png",
    },
    {
        "id": "female_2",
        "label": "柔依 (女模 · 清新甜美)",
        "gender": "female",
        "thumbnail": "/uploads/models/official_model_1.jpg",
        "local_file": "uploads/models/official_model_1.jpg",
        "persona": "fresh and sweet Asian female model in her early 20s, radiant smile, bright expressive eyes, natural healthy glow",
        "fallback_url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250626/ubznva/model_person.png",
    },
    {
        "id": "male_3",
        "label": "Simon (男模 · 混血高级)",
        "gender": "male",
        "thumbnail": "/uploads/models/official_model_4.jpg",
        "local_file": "uploads/models/official_model_4.jpg",
        "persona": "stylish modern Asian model with sharp facial contours, charismatic gaze, contemporary fashionable aura",
        "fallback_url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250626/ubznva/model_person.png",
    },
    {
        "id": "female_3",
        "label": "诗涵 (女模 · 都市摩登)",
        "gender": "female",
        "thumbnail": "/uploads/models/official_model_2.jpg",
        "local_file": "uploads/models/official_model_2.jpg",
        "persona": "chic modern urban Asian female model, minimalist fashion sense, poised demeanor, flawless subtle beauty",
        "fallback_url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250626/ubznva/model_person.png",
    },
    {
        "id": "male_4",
        "label": "宇航 (男模 · 潮酷街头)",
        "gender": "male",
        "thumbnail": "/uploads/models/official_model_8.jpg",
        "local_file": "uploads/models/official_model_8.jpg",
        "persona": "cool athletic East Asian male model, stylish streetwear vibe, toned posture, casual relaxed expression",
        "fallback_url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250626/ubznva/model_person.png",
    },
    {
        "id": "female_4",
        "label": "语晴 (女模 · 元气日常)",
        "gender": "female",
        "thumbnail": "/uploads/models/official_model_5.jpg",
        "local_file": "uploads/models/official_model_5.jpg",
        "persona": "youthful vibrant East Asian female model, natural cheerful smile, approachable chic style",
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


def _get_model_config(model_id: str) -> dict[str, Any]:
    """根据 ID 获取模特配置。"""
    for m in PRESET_MODELS:
        if m["id"] == model_id:
            return m
    return PRESET_MODELS[0]


async def upload_file_to_dashscope_oss(
    file_path: Path,
    api_key: str,
    model_name: str = "aitryon-plus"
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


def _sanitize_garment_image(file_path: Path, category: str) -> Path:
    """
    针对虚拟试穿的单品图像预处理：
    若用户上传的是街拍或模特真人实拍照：
    - 下装 (bottom)：若长宽比过高，裁剪掉顶部多余的上身衣物，防止上衣污染试穿结果；
    - 上装 (top/coat)：若长宽比过高，裁剪掉底部多余的下装，防止下装色彩渗透。
    """
    try:
        from PIL import Image
        with Image.open(file_path) as img:
            w, h = img.size
            if h <= 0 or w <= 0:
                return file_path
            aspect = h / w

            if category == "bottom" and aspect > 1.3:
                cropped = img.crop((0, int(h * 0.18), w, int(h * 0.95)))
                cache_dir = Path("uploads/temp_cleaned")
                cache_dir.mkdir(parents=True, exist_ok=True)
                clean_path = cache_dir / f"clean_{file_path.name}"
                cropped.save(clean_path, quality=95)
                return clean_path

            elif category in ("top", "coat") and aspect > 1.4:
                cropped = img.crop((0, 0, w, int(h * 0.82)))
                cache_dir = Path("uploads/temp_cleaned")
                cache_dir.mkdir(parents=True, exist_ok=True)
                clean_path = cache_dir / f"clean_{file_path.name}"
                cropped.save(clean_path, quality=95)
                return clean_path

    except Exception as e:
        logger.warning(f"图片预处理异常（忽略继续使用原图）: {e}")

    return file_path


async def _resolve_image_to_dashscope_url(
    img_url_or_path: str,
    api_key: str,
    category: str = ""
) -> Optional[str]:
    """将图片本地路径或 URL 转换为 DashScope 可解析的地址。"""
    if not img_url_or_path:
        return None

    if img_url_or_path.startswith("http://") or img_url_or_path.startswith("https://"):
        if "127.0.0.1" not in img_url_or_path and "localhost" not in img_url_or_path:
            return img_url_or_path

    clean_path = img_url_or_path
    if clean_path.startswith("http://127.0.0.1:8000/"):
        clean_path = clean_path.replace("http://127.0.0.1:8000/", "")
    elif clean_path.startswith("/"):
        clean_path = clean_path.lstrip("/")

    local_file = Path(clean_path)
    if not local_file.exists():
        alt_path = Path("apps/api") / clean_path
        if alt_path.exists():
            local_file = alt_path

    if local_file.exists():
        sanitized_file = _sanitize_garment_image(local_file, category)
        return await upload_file_to_dashscope_oss(sanitized_file, api_key)

    logger.warning(f"未能解析本地图片文件: {img_url_or_path}")
    return None


# ── 引擎 1：通义千问超真实人像时尚大片 (Qwen-Image-Plus) ───────────────────────
async def generate_qwen_fashion_lookbook(
    outfit_id: str,
    items: list[dict[str, Any]],
    model_id: str = "male_1",
    scene: str = "daily",
    target_style: str = "casual",
) -> dict[str, Any]:
    """
    调用阿里通义千问生图旗舰大模型 (qwen-image-plus)。
    结合穿搭单品属性、场景环境与选定模特特征，生成超真实人像时尚 Lookbook 大片。
    """
    save_dir = Path("uploads") / "tryon"
    save_dir.mkdir(parents=True, exist_ok=True)

    local_filename = f"{outfit_id}_{model_id}_qwen.png"
    local_filepath = save_dir / local_filename
    local_url = f"/uploads/tryon/{local_filename}"

    if local_filepath.exists() and local_filepath.stat().st_size > 5000:
        logger.info(f"命中 Qwen 生图缓存: {local_url}")
        return {
            "outfit_id": outfit_id,
            "image_url": local_url,
            "model_id": model_id,
            "source": "qwen-image-plus",
            "engine": "qwen",
            "prompt": "qwen-image-plus fashion lookbook",
        }

    api_key = settings.AI_API_KEY
    if not api_key:
        return _error_result(outfit_id, model_id, "未配置 AI_API_KEY，请检查环境变量配置")

    # 构建衣物描述与风格词
    model_cfg = _get_model_config(model_id)
    persona = model_cfg.get("persona", "attractive Asian model, realistic face, natural skin")
    gender = model_cfg.get("gender", "unisex")

    garment_descs = []
    for it in items:
        color = it.get("primary_color", "")
        subcat = it.get("sub_category", "") or it.get("category", "")
        mat = it.get("material", "")
        desc = f"{color} {mat} {subcat}".strip()
        if desc:
            garment_descs.append(desc)

    items_str = ", ".join(garment_descs) if garment_descs else "stylish modern outfit"

    # 场景映射
    scene_map = {
        "commute": "modern urban office building backdrop, clean contemporary city architecture",
        "date": "warm cozy lifestyle cafe, soft ambient bokeh, romantic relaxed atmosphere",
        "sports": "dynamic outdoor sports venue or urban running park, energetic daylight",
        "party": "chic modern celebration venue with subtle evening accent lighting",
        "travel": "picturesque scenic travel destination, natural sunlight, cinematic view",
        "daily": "clean minimalist city street, elegant understated urban background",
    }
    scene_desc = scene_map.get(scene, "tasteful minimalist studio backdrop with soft diffused lighting")

    # 风格映射
    style_map = {
        "casual": "smart casual, relaxed elegance, comfortable modern cut",
        "business": "tailored professional, crisp lines, sophisticated modern business",
        "minimalist": "minimalist aesthetic, clean monochrome palette, pure understated luxury",
        "streetwear": "contemporary street fashion, trendy silhouette, authentic urban cool",
        "vintage": "retro modern chic, timeless appeal, subtle nostalgic warmth",
        "sporty": "sporty athletic chic, functional ergonomic design",
    }
    style_desc = style_map.get(target_style, "refined contemporary fashion style")

    prompt = (
        f"High-end fashion studio lookbook portrait of an {persona}. "
        f"The model is standing and wearing an outfit: {items_str}. "
        f"Style tone: {style_desc}. Setting: {scene_desc}. "
        f"Lighting & Photography: Soft directional key light, gentle natural fill, delicate shadows highlighting natural facial contours, "
        f"ultra-realistic human skin texture with authentic subtle pores and healthy glow, lifelike eyes reflecting soft ambient light, "
        f"natural lip and hair texture. Canon EOS R5 prime lens photography, 8k uhd, cinematic editorial quality, masterpiece photorealism."
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    }

    payload = {
        "model": "qwen-image-plus",
        "input": {"prompt": prompt},
        "parameters": {
            "size": "1024*1024",
            "n": 1,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            submit_resp = await client.post(
                DASHSCOPE_T2I_URL,
                headers=headers,
                json=payload,
            )

            if submit_resp.status_code != 200:
                err_text = submit_resp.text
                logger.error(f"qwen-image-plus 提交失败 HTTP {submit_resp.status_code}: {err_text}")
                # 尝试降级至 aitryon
                logger.info("尝试自动降级至 aitryon 试衣引擎...")
                return await generate_virtual_tryon(
                    outfit_id=outfit_id,
                    items=items,
                    model_id=model_id,
                    scene=scene,
                    target_style=target_style,
                )

            task_id = submit_resp.json().get("output", {}).get("task_id")
            if not task_id:
                return _error_result(outfit_id, model_id, f"未能获取 task_id: {submit_resp.text[:120]}")

            logger.info(f"Qwen 生图任务提交成功: task_id={task_id}")

            generated_img_url: Optional[str] = None
            poll_headers = {"Authorization": f"Bearer {api_key}"}

            for i in range(25):
                await asyncio.sleep(2.0)
                poll_resp = await client.get(
                    f"{DASHSCOPE_TASK_URL}/{task_id}",
                    headers=poll_headers,
                    timeout=10.0,
                )
                if poll_resp.status_code != 200:
                    continue

                poll_data = poll_resp.json()
                task_status = poll_data.get("output", {}).get("task_status")

                if task_status == "SUCCEEDED":
                    results = poll_data.get("output", {}).get("results", [])
                    if results and "url" in results[0]:
                        generated_img_url = results[0]["url"]
                    elif "image_url" in poll_data.get("output", {}):
                        generated_img_url = poll_data.get("output", {}).get("image_url")
                    break
                elif task_status in ("FAILED", "CANCELED"):
                    err_msg = poll_data.get("output", {}).get("message", "任务执行异常")
                    logger.error(f"Qwen 生图任务失败: {err_msg}")
                    return _error_result(outfit_id, model_id, f"Qwen 生图失败: {err_msg}")

            if generated_img_url:
                dl_resp = await client.get(generated_img_url, timeout=30.0)
                if dl_resp.status_code == 200:
                    local_filepath.write_bytes(dl_resp.content)
                    logger.info(f"Qwen 时尚大片已保存至: {local_url}")
                    return {
                        "outfit_id": outfit_id,
                        "image_url": local_url,
                        "model_id": model_id,
                        "source": "qwen-image-plus",
                        "engine": "qwen",
                        "prompt": prompt[:120] + "...",
                    }
                else:
                    return _error_result(outfit_id, model_id, f"下载大片结果失败 (HTTP {dl_resp.status_code})")

    except httpx.TimeoutException:
        return _error_result(outfit_id, model_id, "Qwen 生图请求超时，请检查网络")
    except Exception as e:
        logger.error(f"Qwen 生图异常: {e}", exc_info=True)
        return _error_result(outfit_id, model_id, f"生图服务异常: {str(e)}")

    return _error_result(outfit_id, model_id, "Qwen 生图超时，请稍后重试")


# ── 引擎 2：百炼高保真虚拟试衣 (OutfitAnyone aitryon-plus) ─────────────────────
async def generate_virtual_tryon(
    outfit_id: str,
    items: list[dict[str, Any]],
    model_id: str = "male_1",
    scene: str = "daily",
    target_style: str = "casual",
) -> dict[str, Any]:
    """
    调用阿里云百炼 OutfitAnyone (aitryon-plus) 虚拟试穿大模型。
    将搭配中的真实平铺图 1:1 迁移贴合到选定模特身上。
    """
    save_dir = Path("uploads") / "tryon"
    save_dir.mkdir(parents=True, exist_ok=True)

    local_filename = f"{outfit_id}_{model_id}_aitryon.jpg"
    local_filepath = save_dir / local_filename
    local_url = f"/uploads/tryon/{local_filename}"

    if local_filepath.exists() and local_filepath.stat().st_size > 5000:
        logger.info(f"命中 aitryon 试穿缓存: {local_url}")
        return {
            "outfit_id": outfit_id,
            "image_url": local_url,
            "model_id": model_id,
            "source": "aitryon-plus",
            "engine": "aitryon",
        }

    api_key = settings.AI_API_KEY
    if not api_key:
        return _error_result(outfit_id, model_id, "未配置 AI_API_KEY，请检查环境变量配置")

    # 1. 准备模特图
    model_cfg = _get_model_config(model_id)
    local_model_path = Path(model_cfg["local_file"])
    person_image_url = None

    if local_model_path.exists():
        person_image_url = await upload_file_to_dashscope_oss(local_model_path, api_key, model_name="aitryon-plus")

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
            top_garment_url = await _resolve_image_to_dashscope_url(img, api_key, category=cat)
        elif cat == "bottom" and not bottom_garment_url:
            bottom_garment_url = await _resolve_image_to_dashscope_url(img, api_key, category=cat)

    if not top_garment_url and not bottom_garment_url:
        return _error_result(outfit_id, model_id, "搭配方案中无可识别的衣物图片，无法发起试穿")

    logger.info(
        f"发起 OutfitAnyone Plus 试穿: outfit={outfit_id}, model={model_id}, "
        f"top={'有' if top_garment_url else '无'}, bottom={'有' if bottom_garment_url else '无'}"
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
        "model": "aitryon-plus",
        "input": input_payload,
        "parameters": {
            "resolution": -1,
            "restore_face": True,
        }
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            submit_resp = await client.post(
                DASHSCOPE_SYNTHESIS_URL,
                headers=headers,
                json=payload,
            )

            if submit_resp.status_code != 200:
                err_text = submit_resp.text
                logger.error(f"aitryon-plus 提交失败 HTTP {submit_resp.status_code}: {err_text}")
                return _error_result(outfit_id, model_id, f"试穿任务提交失败: {err_text[:120]}")

            task_id = submit_resp.json().get("output", {}).get("task_id")
            if not task_id:
                return _error_result(outfit_id, model_id, f"未能获取试穿 task_id: {submit_resp.text[:120]}")

            logger.info(f"aitryon-plus 试衣任务已提交: task_id={task_id}")

            poll_headers = {"Authorization": f"Bearer {api_key}"}
            generated_img_url: Optional[str] = None

            for i in range(25):
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
                    logger.error(f"aitryon-plus 任务失败: {err_msg}")
                    return _error_result(outfit_id, model_id, f"试衣生成失败: {err_msg}")

            if generated_img_url:
                dl_resp = await client.get(generated_img_url, timeout=30.0)
                if dl_resp.status_code == 200:
                    local_filepath.write_bytes(dl_resp.content)
                    logger.info(f"aitryon-plus 试穿效果图已保存至: {local_url}")
                    return {
                        "outfit_id": outfit_id,
                        "image_url": local_url,
                        "model_id": model_id,
                        "source": "aitryon-plus",
                        "engine": "aitryon",
                    }
                else:
                    return _error_result(outfit_id, model_id, f"结果图拉取失败 (HTTP {dl_resp.status_code})")

    except httpx.TimeoutException:
        return _error_result(outfit_id, model_id, "请求超时，请检查网络或稍后重试")
    except Exception as e:
        logger.error(f"虚拟试穿执行异常: {e}", exc_info=True)
        return _error_result(outfit_id, model_id, f"虚拟试穿服务异常: {str(e)}")

    return _error_result(outfit_id, model_id, "试穿生成超时，请稍后重试")


def _error_result(outfit_id: str, model_id: str, error: str) -> dict[str, Any]:
    """统一错误返回。"""
    return {
        "outfit_id": outfit_id,
        "image_url": "",
        "model_id": model_id,
        "source": "error",
        "engine": "unknown",
        "error": error,
    }


# ── 综合统一调度接口 ────────────────────────────────────────────────────────
async def generate_tryon_image(
    outfit_id: str,
    items: list[dict[str, Any]],
    gender: str = "unisex",
    scene: str = "daily",
    target_style: str = "casual",
    model_id: str = "male_1",
    engine: str = "qwen",
) -> dict[str, Any]:
    """
    生图/试衣统一入口。
    - engine="qwen": 阿里通义千问超真实人像时尚写真（默认推荐，真实人脸、光影景深、高颜值）
    - engine="aitryon": 阿里百炼 OutfitAnyone Plus 1:1 像素级虚拟试穿
    """
    if gender == "male" and model_id == "female_1":
        model_id = "male_1"

    if engine == "aitryon":
        result = await generate_virtual_tryon(
            outfit_id=outfit_id,
            items=items,
            model_id=model_id,
            scene=scene,
            target_style=target_style,
        )
    else:
        result = await generate_qwen_fashion_lookbook(
            outfit_id=outfit_id,
            items=items,
            model_id=model_id,
            scene=scene,
            target_style=target_style,
        )

    result.setdefault("prompt", f"{engine} fashion generation")
    return result
