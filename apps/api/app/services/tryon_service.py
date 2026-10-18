"""
AI 虚拟试穿与时尚生图服务 (Virtual Try-On & Fashion Generation Service)。

支持双生图引擎：
1. 🌟 通义万相 2.1 旗舰写真大片 (wanx2.1-t2i-plus / wanx2.1-t2i-turbo)：
   - 基于搭配中单品的材质、版型、色彩与穿搭场景，生成超真实自然人像时尚大片。
   - 具备真实皮肤质感、自然微表情、发丝光影和单反景深，彻底告别假面与畸变。
   - 支持根据用户上传的全身照专属特征进行量身定制。
2. 👗 百炼高保真虚拟试衣 (OutfitAnyone aitryon-plus)：
   - 基于用户衣橱真实平铺图片（通过百炼官方通道自动上传至临时 OSS 进行解析）。
   - 1:1 提取服装材质与版型精确贴合至选定的模特身姿或用户自定义人像身姿。
"""
import asyncio
import json
import logging
import os
import shutil
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


# ── 官方精选预设模特图库 (精简为 2 位核心专业男女模特) ─────────────────────
PRESET_MODELS = [
    {
        "id": "female_1",
        "label": "雅琪 (女模 · 优雅知性)",
        "gender": "female",
        "thumbnail": "/uploads/models/official_model_6.jpg",
        "local_file": "uploads/models/official_model_6.jpg",
        "persona": "elegant and graceful East Asian female model in her 20s, sophisticated natural makeup, soft smile, gentle refined features, radiant fair skin",
        "fallback_url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250626/ubznva/model_person.png",
    },
    {
        "id": "male_1",
        "label": "小轩 (男模 · 阳光俊朗)",
        "gender": "male",
        "thumbnail": "/uploads/models/official_model_16.jpg",
        "local_file": "uploads/models/official_model_16.jpg",
        "persona": "handsome and confident East Asian young male model in his 20s, clean-shaven, sharp jawline, natural friendly expression, stylish haircut",
        "fallback_url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250626/ubznva/model_person.png",
    },
]

# 内存级 OSS URL 缓存 (避免同张图片重复上传, key: local_path, val: oss://...)
_OSS_CACHE: dict[str, str] = {}


# ── 用户自定义模特管理 ──────────────────────────────────────────────────────
def get_user_custom_model_dir(user_id: str) -> Path:
    """获取用户自定义模特存储目录。"""
    user_str = str(user_id).strip() or "default_user"
    p = Path("uploads") / "user_models" / user_str
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_user_custom_model(user_id: Optional[str]) -> Optional[dict[str, Any]]:
    """读取指定用户的自定义全身照模特配置。"""
    if not user_id:
        return None
    user_dir = get_user_custom_model_dir(user_id)
    meta_file = user_dir / "model_meta.json"
    if meta_file.exists():
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            local_p = Path(data.get("local_file", ""))
            if not local_p.exists():
                alt_p = Path("apps/api") / data.get("local_file", "")
                if alt_p.exists():
                    local_p = alt_p
            if local_p.exists():
                return data
        except Exception as e:
            logger.warning(f"读取用户自定义模特配置失败: {e}")
    return None


def save_user_custom_model(
    user_id: str,
    image_bytes: bytes,
    file_ext: str,
    gender: str = "female",
    persona: str = "",
    hairstyle: str = "保持原图自然发型与发色",
    body_shape: str = "真实自然身材比例",
) -> dict[str, Any]:
    """保存用户上传的全身照并写入元数据，锁定发型与真实身材。"""
    user_dir = get_user_custom_model_dir(user_id)
    # 清理历史可能存在的旧图片及旧遮罩
    for old_file in user_dir.glob("custom_model.*"):
        try:
            old_file.unlink()
        except Exception:
            pass
    old_mask = user_dir / "clothing_mask.png"
    if old_mask.exists():
        try:
            old_mask.unlink()
        except Exception:
            pass

    clean_ext = file_ext if file_ext.startswith(".") else f".{file_ext}"
    img_name = f"custom_model{clean_ext}"
    local_path = user_dir / img_name
    local_path.write_bytes(image_bytes)

    rel_local = str(local_path).replace("\\", "/")
    web_url = f"/uploads/user_models/{user_id}/{img_name}"

    model_data = {
        "id": "custom",
        "label": "我的形象 (真人专属)",
        "gender": gender,
        "thumbnail": web_url,
        "full_url": web_url,
        "local_file": rel_local,
        "persona": persona or "真实自然东亚年轻人物，自然健康肤质与神态",
        "hairstyle": hairstyle or "保持原图自然发型与发色",
        "body_shape": body_shape or "真实自然身材比例",
        "is_custom": True,
        "has_uploaded": True,
    }

    meta_file = user_dir / "model_meta.json"
    meta_file.write_text(json.dumps(model_data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"成功保存用户 {user_id} 的自定义模特: {web_url}")
    return model_data


def delete_user_custom_model(user_id: str) -> bool:
    """删除用户的自定义模特。"""
    user_dir = get_user_custom_model_dir(user_id)
    if user_dir.exists():
        shutil.rmtree(user_dir, ignore_errors=True)
        return True
    return False


async def generate_clean_background_model(
    user_id: str,
    use_ai_model: bool = True,
) -> dict[str, Any]:
    """
    当用户上传的全身照背景杂乱时，调用百炼万相大模型 (wanx2.1-imageedit) 或精细人像算法，
    生成一个背景 100% 纯白干净的高级无缝影棚用户画像图，供后续试穿与Lookbook使用。
    """
    user_dir = get_user_custom_model_dir(user_id)
    meta_file = user_dir / "model_meta.json"
    if not meta_file.exists():
        raise RuntimeError("未找到该用户的自定义模特配置")

    with open(meta_file, "r", encoding="utf-8") as f:
        model_data = json.load(f)

    # 优先获取原始上传图片
    raw_path_str = model_data.get("local_raw_file") or model_data.get("local_file", "")
    raw_path = Path(raw_path_str)
    if not raw_path.exists():
        alt_path = Path("apps/api") / raw_path_str
        if alt_path.exists():
            raw_path = alt_path

    if not raw_path.exists():
        candidates = [p for p in user_dir.glob("custom_model.*") if "_white" not in p.name and "mask" not in p.name]
        if candidates:
            raw_path = candidates[0]
        else:
            raise RuntimeError(f"未找到用户上传的原图文件: {user_dir}")

    white_filename = "custom_model_white.png"
    white_local_path = user_dir / white_filename
    white_web_url = f"/uploads/user_models/{user_id}/{white_filename}"
    rel_white_local = str(white_local_path).replace("\\", "/")

    # 1. 尝试使用百炼万相 wanx2.1-imageedit 大模型进行专业影棚纯白背景重绘
    api_key = settings.AI_API_KEY
    success_with_ai = False

    if use_ai_model and api_key:
        try:
            from PIL import Image, ImageFilter
            import numpy as np
            from rembg import remove, new_session
            import cv2
            import base64
            import httpx

            orig_img = Image.open(raw_path).convert("RGB")
            session = new_session("u2net_human_seg")
            human_mask = remove(orig_img, session=session, only_mask=True)
            mask_arr = np.array(human_mask)

            # 人物区域为 0 (锁定)，背景区域为 255 (重绘)
            bg_mask_arr = np.where(mask_arr > 128, 0, 255).astype(np.uint8)
            kernel = np.ones((5, 5), np.uint8)
            bg_mask_dilated = cv2.dilate(bg_mask_arr, kernel, iterations=1)
            bg_mask_img = Image.fromarray(bg_mask_dilated).filter(ImageFilter.GaussianBlur(radius=2))

            bg_mask_path = user_dir / "background_mask.png"
            bg_mask_img.save(bg_mask_path)

            b64_base = "data:image/jpeg;base64," + base64.b64encode(raw_path.read_bytes()).decode("utf-8")
            b64_mask = "data:image/png;base64," + base64.b64encode(bg_mask_path.read_bytes()).decode("utf-8")

            prompt = (
                "专业时尚服装模特商业摄影，背景为100%纯白色无缝摄影棚空白背景，高调纯净，干净无瑕，"
                "高级摄影棚柔和均匀布光，极简纯白影棚地面带有模特自然的微弱脚底接触阴影，"
                "完全没有任何家具、无杂物、无门窗、无帘子、无任何多余装饰，"
                "严禁修改模特人物、严禁修改人物五官、眼镜、发型、体态、服装与鞋子"
            )

            payload = {
                "model": "wanx2.1-imageedit",
                "input": {
                    "function": "description_edit_with_mask",
                    "base_image_url": b64_base,
                    "mask_image_url": b64_mask,
                    "prompt": prompt,
                },
                "parameters": {"n": 1},
            }

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "X-DashScope-Async": "enable",
            }

            async with httpx.AsyncClient(timeout=35.0) as client:
                submit_resp = await client.post(
                    DASHSCOPE_SYNTHESIS_URL,
                    headers=headers,
                    json=payload,
                )
                if submit_resp.status_code == 200:
                    task_id = submit_resp.json().get("output", {}).get("task_id")
                    if task_id:
                        poll_url = f"{DASHSCOPE_TASK_URL}/{task_id}"
                        poll_headers = {"Authorization": f"Bearer {api_key}"}
                        for _ in range(25):
                            await asyncio.sleep(2.5)
                            poll_resp = await client.get(poll_url, headers=poll_headers, timeout=20.0)
                            if poll_resp.status_code == 200:
                                p_data = poll_resp.json()
                                status = p_data.get("output", {}).get("task_status")
                                if status == "SUCCEEDED":
                                    img_url = p_data.get("output", {}).get("results", [{}])[0].get("url")
                                    if img_url:
                                        for _retry in range(3):
                                            try:
                                                dl_resp = await client.get(img_url, timeout=30.0)
                                                if dl_resp.status_code == 200:
                                                    white_local_path.write_bytes(dl_resp.content)
                                                    success_with_ai = True
                                                    logger.info(f"万相大模型成功生成纯白影棚画像图: {white_local_path}")
                                                    break
                                            except Exception as dl_err:
                                                logger.warning(f"下载纯白生图重试: {dl_err}")
                                                await asyncio.sleep(1.5)
                                    break
                                elif status in ("FAILED", "CANCELED"):
                                    logger.warning(f"万相纯白背景任务状态为 {status}")
                                    break
        except Exception as e:
            logger.warning(f"万相背景大模型生成遇到异常: {e}，将平滑降级至高保真纯白影棚合成")

    # 2. 若 AI 生成未成功或未启用，使用 rembg 高保真平滑纯白影棚合成兜底
    if not success_with_ai or not white_local_path.exists() or white_local_path.stat().st_size < 5000:
        logger.info("执行 rembg 人像高保真纯白影棚背景合成...")
        from PIL import Image, ImageFilter
        import numpy as np
        from rembg import remove, new_session

        orig_img = Image.open(raw_path).convert("RGB")
        w, h = orig_img.size
        session = new_session("u2net_human_seg")
        person_rgba = remove(orig_img, session=session)
        alpha = person_rgba.split()[-1]
        smooth_alpha = alpha.filter(ImageFilter.GaussianBlur(radius=1.0))

        white_bg = Image.new("RGB", (w, h), (255, 255, 255))

        # 地面接触阴影
        alpha_arr = np.array(alpha)
        bottom_y = int(h * 0.88)
        feet_mask_arr = np.zeros_like(alpha_arr)
        feet_mask_arr[bottom_y:, :] = alpha_arr[bottom_y:, :]
        feet_shadow = Image.fromarray(feet_mask_arr).filter(ImageFilter.GaussianBlur(radius=12))
        white_bg.paste(Image.new("RGB", (w, h), (225, 225, 230)), (0, 0), feet_shadow)

        white_bg.paste(person_rgba, (0, 0), smooth_alpha)
        white_bg.save(white_local_path, quality=95)
        logger.info(f"rembg 高保真纯白背景画像已生成: {white_local_path}")

    # 3. 更新用户元数据配置
    model_data["white_url"] = white_web_url
    model_data["local_white_file"] = rel_white_local
    model_data["has_clean_white"] = True
    model_data["active_display"] = "white"
    model_data["thumbnail"] = white_web_url
    model_data["full_url"] = white_web_url
    model_data["local_file"] = rel_white_local

    meta_file.write_text(json.dumps(model_data, ensure_ascii=False, indent=2), encoding="utf-8")

    # 4. 重新基于纯白图生成并缓存高质量服装遮罩
    try:
        get_or_create_clothing_mask(white_local_path)
    except Exception as me:
        logger.warning(f"生成纯白模特遮罩警告: {me}")

    return model_data


def switch_user_model_display(user_id: str, mode: str = "white") -> dict[str, Any]:
    """切换用户自定义模特的显示底图：'white' (纯白影棚背景) 或 'raw' (原拍照背景)。"""
    user_dir = get_user_custom_model_dir(user_id)
    meta_file = user_dir / "model_meta.json"
    if not meta_file.exists():
        raise RuntimeError("未找到该用户的自定义模特配置")

    with open(meta_file, "r", encoding="utf-8") as f:
        model_data = json.load(f)

    raw_url = model_data.get("raw_url") or model_data.get("thumbnail", "")
    raw_local = model_data.get("local_raw_file") or model_data.get("local_file", "")
    white_url = model_data.get("white_url", "")
    white_local = model_data.get("local_white_file", "")

    if mode == "white" and white_url:
        p = Path(white_local)
        if not p.exists():
            alt = Path("apps/api") / white_local
            if alt.exists():
                p = alt
        if p.exists():
            model_data["active_display"] = "white"
            model_data["thumbnail"] = white_url
            model_data["full_url"] = white_url
            model_data["local_file"] = white_local
            meta_file.write_text(json.dumps(model_data, ensure_ascii=False, indent=2), encoding="utf-8")
            return model_data

    # 回退到原始图片
    model_data["active_display"] = "raw"
    model_data["thumbnail"] = raw_url
    model_data["full_url"] = raw_url
    model_data["local_file"] = raw_local
    meta_file.write_text(json.dumps(model_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return model_data


def get_preset_models(user_id: Optional[str] = None) -> list[dict[str, Any]]:
    """返回模特图列表供前端选择：置顶自定义卡片 + 精简的 2 位核心专业男女模特。"""
    result: list[dict[str, Any]] = []

    # 1. 尝试获取用户专属模特
    custom = get_user_custom_model(user_id) if user_id else None
    if custom:
        active_thumb = custom.get("thumbnail", "")
        raw_thumb = custom.get("raw_url") or active_thumb
        white_thumb = custom.get("white_url", "")
        result.append({
            "id": "custom",
            "label": custom.get("label", "我的形象 (真人专属)"),
            "gender": custom.get("gender", "male"),
            "thumbnail": active_thumb,
            "full_url": active_thumb,
            "raw_url": raw_thumb,
            "white_url": white_thumb,
            "has_clean_white": custom.get("has_clean_white", False),
            "active_display": custom.get("active_display", "raw"),
            "hairstyle": custom.get("hairstyle", "保持原图自然发型与发色"),
            "body_shape": custom.get("body_shape", "真实自然身材比例"),
            "is_custom": True,
            "has_uploaded": True,
        })
    else:
        result.append({
            "id": "custom",
            "label": "我的形象 (点击上传)",
            "gender": "unisex",
            "thumbnail": "",
            "full_url": "",
            "raw_url": "",
            "white_url": "",
            "has_clean_white": False,
            "active_display": "raw",
            "hairstyle": "保持原图自然发型",
            "body_shape": "真实自然身材",
            "is_custom": True,
            "has_uploaded": False,
        })


    # 2. 预设核心模特
    for m in PRESET_MODELS:
        result.append({
            "id": m["id"],
            "label": m["label"],
            "gender": m["gender"],
            "thumbnail": m["thumbnail"],
            "full_url": m["thumbnail"],
            "is_custom": False,
            "has_uploaded": True,
        })

    return result


def _get_model_config(model_id: str, user_id: Optional[str] = None) -> dict[str, Any]:
    """根据 ID 获取模特配置（支持 custom 自定义模特与预设模特）。"""
    if model_id == "custom":
        custom = get_user_custom_model(user_id)
        if custom:
            return custom
        # 用户尚未上传时，回退到首位预设模特
        return PRESET_MODELS[0]

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
    返回形如 'oss://...' 的地址，可在调用 DashScope 模型时直接传参。
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
    """针对单品图像的裁剪预处理（下装除顶，上装除底，防止色彩串染）。"""
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


# ── 引擎 1：通义万相 2.1 旗舰写真大片 (wanx2.1-t2i-plus) ──────────────────────
async def generate_qwen_fashion_lookbook(
    outfit_id: str,
    items: list[dict[str, Any]],
    model_id: str = "female_1",
    scene: str = "daily",
    target_style: str = "casual",
    user_id: Optional[str] = None,
) -> dict[str, Any]:
    """
    调用阿里通义万相 2.1 旗舰生图大模型 (wanx2.1-t2i-plus / wanx2.1-t2i-turbo)。
    结合穿搭单品属性、场景环境与选定模特/用户真实人像特征，生成超真实人像时尚 Lookbook 大片。
    """
    save_dir = Path("uploads") / "tryon"
    save_dir.mkdir(parents=True, exist_ok=True)

    cache_suffix = f"{outfit_id}_{model_id}"
    if model_id == "custom" and user_id:
        cache_suffix += f"_{user_id[:8]}"
    local_filename = f"{cache_suffix}_purewhite_v2.png"
    local_filepath = save_dir / local_filename
    local_url = f"/uploads/tryon/{local_filename}"

    if local_filepath.exists() and local_filepath.stat().st_size > 5000:
        logger.info(f"命中万相生图缓存: {local_url}")
        return {
            "outfit_id": outfit_id,
            "image_url": local_url,
            "model_id": model_id,
            "source": "wanx2.1-t2i-plus",
            "engine": "qwen",
            "prompt": "wanx2.1 pure-white studio lookbook",
        }

    api_key = settings.AI_API_KEY
    if not api_key:
        return _error_result(outfit_id, model_id, "未配置 AI_API_KEY，请检查环境变量配置")

    # 1. 模特人像与发型身材约束 (严密保持原图发型发色，严格保持真实身材，杜绝形变与夸张头身比)
    model_cfg = _get_model_config(model_id, user_id=user_id)
    gender = model_cfg.get("gender", "female")
    gender_zh = "女性" if gender == "female" else "男性"

    if model_id == "custom":
        hairstyle_str = model_cfg.get("hairstyle") or "保持原图自然发型与发色，严格保持原图发长与发际线，严禁擅自修改发型或增加烫染卷发"
        body_str = model_cfg.get("body_shape") or "严格保持原图真实身材与骨骼比例，真实日常人体比例，拒绝夸张头身比，拒绝AI过度瘦身或体型形变"
        person_str = f"真实自然的东亚年轻{gender_zh}，{hairstyle_str}，真实自然的面容神态与细腻人脸皮肤质感，{body_str}，自然端正站姿"
    elif model_id == "female_1":
        person_str = "真实自然、优雅知性的东亚年轻女性模特，原图黑色齐肩直发与自然发际线，清秀面容与细腻皮肤质感，真实自然匀称身材，自然端正立姿"
    else:
        person_str = "阳光俊朗的东亚年轻男性模特，原图干净利落黑色短发，清爽干净的面容轮廓与真实皮肤质感，真实自然体态比例，自然端正立姿"

    # 2. 纯净背景约束 (严格空白背景/纯白无缝影棚，杜绝任何杂乱街景与道具)
    bg_str = "背景：纯白无缝影棚单色背景，高调纯净，纯白色空白背景，完全没有任何背景杂物、无家具、无建筑、无户外街景、无多余道具"

    # 3. 搭配单品描述 (严格按照搭配清单精准还原色彩与材质款式)
    color_zh_map = {
        "white": "白色", "black": "黑色", "blue": "深蓝色", "navy": "藏青色",
        "gray": "灰色", "grey": "灰色", "beige": "米色", "khaki": "卡其色",
        "brown": "棕色", "red": "红色", "green": "墨绿色", "yellow": "黄色",
        "pink": "淡粉色", "purple": "紫色", "orange": "橘色"
    }

    garments = []
    for it in items:
        color = it.get("primary_color", "")
        color_zh = color_zh_map.get(str(color).lower(), color)
        subcat = it.get("sub_category") or it.get("category", "")
        mat = it.get("material", "")
        desc = f"{color_zh}{mat}{subcat}".strip()
        if desc:
            garments.append(desc)
    garments_str = "，".join(garments) if garments else "整洁大方的日常服饰"

    # 4. 严禁多余饰品、严禁多余配件 (负向强制排除)
    restriction_str = (
        "画面严格限制：画面中严禁出现任何多余配饰，绝对不要帽子、棒球帽、墨镜、眼镜、项链、耳环、手镯、手链、手表、"
        "手提包、单肩包、斜挎包、双肩包，严禁擅自添加清单以外的外套、围巾或手持道具。模特仅穿戴指定的搭配服饰，画面干净纯粹"
    )

    # 5. 摄影参数 (85mm定焦大师级单反画质，f/8光圈全身清晰对焦)
    photo_str = "顶级服装商业画册大片，85mm人像定焦镜头，f/8光圈全身清晰对焦，柔和均匀影棚高调光，8K超清画质，真实商业摄影质感"

    prompt = f"专业服装模特商业摄影，全身立姿照。{bg_str}。出镜人物：{person_str}。身着服饰搭配：{garments_str}。{restriction_str}。{photo_str}"
    logger.info(f"Wanx 2.1 纯净定制 Prompt: {prompt}")


    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    }

    # 优先使用 wanx2.1-t2i-plus，如遇限流备用 wanx2.1-t2i-turbo
    candidate_models = ["wanx2.1-t2i-plus", "wanx2.1-t2i-turbo"]

    async with httpx.AsyncClient(timeout=35.0) as client:
        last_err = ""
        for model_name in candidate_models:
            payload = {
                "model": model_name,
                "input": {"prompt": prompt},
                "parameters": {
                    "size": "1024*1024",
                    "n": 1,
                },
            }

            try:
                submit_resp = await client.post(
                    DASHSCOPE_T2I_URL,
                    headers=headers,
                    json=payload,
                )

                if submit_resp.status_code != 200:
                    last_err = submit_resp.text
                    logger.warning(f"{model_name} 提交失败 HTTP {submit_resp.status_code}: {last_err}")
                    continue

                task_id = submit_resp.json().get("output", {}).get("task_id")
                if not task_id:
                    last_err = submit_resp.text
                    continue

                logger.info(f"{model_name} 生图任务提交成功: task_id={task_id}")

                generated_img_url: Optional[str] = None
                poll_headers = {"Authorization": f"Bearer {api_key}"}

                for _ in range(25):
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
                        logger.error(f"{model_name} 任务失败: {err_msg}")
                        last_err = err_msg
                        break

                if generated_img_url:
                    dl_resp = await client.get(generated_img_url, timeout=30.0)
                    if dl_resp.status_code == 200:
                        local_filepath.write_bytes(dl_resp.content)
                        logger.info(f"万相时尚大片已保存至: {local_url}")
                        return {
                            "outfit_id": outfit_id,
                            "image_url": local_url,
                            "model_id": model_id,
                            "source": model_name,
                            "engine": "qwen",
                            "prompt": prompt[:120] + "...",
                        }

            except Exception as e:
                logger.error(f"{model_name} 生图异常: {e}")
                last_err = str(e)

        return _error_result(outfit_id, model_id, f"AI 生图生成暂时失败: {last_err[:120]}")


# ── 引擎 2：百炼高保真虚拟试衣 (OutfitAnyone aitryon-plus) ─────────────────────
async def generate_virtual_tryon(
    outfit_id: str,
    items: list[dict[str, Any]],
    model_id: str = "female_1",
    scene: str = "daily",
    target_style: str = "casual",
    user_id: Optional[str] = None,
) -> dict[str, Any]:
    """
    调用阿里云百炼 OutfitAnyone (aitryon-plus) 虚拟试穿大模型。
    若服务异常或未授权，自动平滑无缝降级至万相 2.1 旗舰大片生图，确保体验绝不中断。
    """
    save_dir = Path("uploads") / "tryon"
    save_dir.mkdir(parents=True, exist_ok=True)

    cache_suffix = f"{outfit_id}_{model_id}"
    if model_id == "custom" and user_id:
        cache_suffix += f"_{user_id[:8]}"
    local_filename = f"{cache_suffix}_aitryon.jpg"
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

    # 1. 准备模特图（支持自定义真人照片与预设模特）
    model_cfg = _get_model_config(model_id, user_id=user_id)
    local_model_path = Path(model_cfg.get("local_file", ""))
    if not local_model_path.exists():
        alt_path = Path("apps/api") / model_cfg.get("local_file", "")
        if alt_path.exists():
            local_model_path = alt_path

    person_image_url: Optional[str] = None
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
        logger.info("搭配中无单品平铺图，自动切换至万相旗舰生图...")
        return await generate_qwen_fashion_lookbook(
            outfit_id=outfit_id,
            items=items,
            model_id=model_id,
            scene=scene,
            target_style=target_style,
            user_id=user_id,
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

            # 若 aitryon 接口调用受限（如未开通 aitryon-plus 权限），无缝平滑回退至万相生图
            if submit_resp.status_code != 200:
                logger.warning(
                    f"aitryon-plus 试穿提交未成功 (HTTP {submit_resp.status_code}): {submit_resp.text}，"
                    "已无缝平滑回退至通义万相旗舰生图..."
                )
                return await generate_qwen_fashion_lookbook(
                    outfit_id=outfit_id,
                    items=items,
                    model_id=model_id,
                    scene=scene,
                    target_style=target_style,
                    user_id=user_id,
                )

            task_id = submit_resp.json().get("output", {}).get("task_id")
            if not task_id:
                logger.warning("未能获取 aitryon task_id，自动回退至万相生图...")
                return await generate_qwen_fashion_lookbook(
                    outfit_id=outfit_id,
                    items=items,
                    model_id=model_id,
                    scene=scene,
                    target_style=target_style,
                    user_id=user_id,
                )

            logger.info(f"aitryon-plus 试衣任务已提交: task_id={task_id}")

            poll_headers = {"Authorization": f"Bearer {api_key}"}
            generated_img_url: Optional[str] = None

            for _ in range(25):
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
                    logger.warning(f"aitryon-plus 任务失败: {err_msg}，回退至万相生图...")
                    return await generate_qwen_fashion_lookbook(
                        outfit_id=outfit_id,
                        items=items,
                        model_id=model_id,
                        scene=scene,
                        target_style=target_style,
                        user_id=user_id,
                    )

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

    except Exception as e:
        logger.warning(f"虚拟试穿执行异常: {e}，自动回退至万相生图...")
        return await generate_qwen_fashion_lookbook(
            outfit_id=outfit_id,
            items=items,
            model_id=model_id,
            scene=scene,
            target_style=target_style,
            user_id=user_id,
        )

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


def get_or_create_clothing_mask(image_path: Path) -> Path:
    """
    自动提取并缓存服装区域遮罩（黑白蒙版）：
    - 黑色区域 (0): 头部、头发、面容、五官、手部姿势、背景、鞋履 100% 冻结保护！
    - 白色区域 (255): 仅上装与下装等衣服区域，允许局部重绘换装。
    """
    mask_path = image_path.parent / "clothing_mask.png"
    if mask_path.exists() and mask_path.stat().st_size > 500:
        return mask_path

    try:
        from rembg import remove, new_session
        from PIL import Image, ImageFilter
        import numpy as np

        orig_img = Image.open(image_path).convert("RGB")
        w, h = orig_img.size

        session = new_session("u2net_human_seg")
        human_mask = remove(orig_img, session=session, only_mask=True)
        mask_arr = np.array(human_mask)

        # 1. 保护头部、发型、面容、耳朵 (Top 22% 强制涂黑锁定保护)
        head_cutoff = int(h * 0.22)
        mask_arr[:head_cutoff, :] = 0

        # 2. 脖子柱状与咽喉喉结精准保护 (中央 41%~58% 区域一直保护至领口 29.8% 高度)
        # 彻底避免将用户的喉结与自然颈部肌肤误当成衣服挖空，杜绝假领、假脖子与紧绷感
        neck_x1 = int(w * 0.41)
        neck_x2 = int(w * 0.58)
        neck_y_bottom = int(h * 0.298)
        mask_arr[:neck_y_bottom, neck_x1:neck_x2] = 0

        # 3. 两肩斜方肌外侧在 22%~24.5% 之间保护背景布，避免背景杂色侵入
        mask_arr[int(h * 0.22):int(h * 0.245), :neck_x1] = 0
        mask_arr[int(h * 0.22):int(h * 0.245), neck_x2:] = 0

        # 4. 保护脚部、鞋履 (Bottom 8% 强制涂黑锁定保护)
        feet_cutoff = int(h * 0.92)
        mask_arr[feet_cutoff:, :] = 0

        clothing_mask = Image.fromarray(mask_arr)
        # 边缘适度高斯模糊羽化（半径 3），确保新衣物接缝处如单反拍摄般自然柔和融合
        clothing_mask = clothing_mask.filter(ImageFilter.GaussianBlur(radius=3))
        clothing_mask.save(mask_path)
        logger.info(f"成功生成解剖学精准服装遮罩: {mask_path}")
        return mask_path
    except Exception as e:
        logger.warning(f"基于 rembg 生成遮罩遇到问题: {e}，使用人体工学比例遮罩兜底")
        try:
            from PIL import Image, ImageDraw, ImageFilter
            orig_img = Image.open(image_path)
            w, h = orig_img.size
            fallback_mask = Image.new("L", (w, h), 0)
            draw = ImageDraw.Draw(fallback_mask)
            # 躯干与下装中心区域
            draw.rectangle([int(w * 0.22), int(h * 0.22), int(w * 0.78), int(h * 0.90)], fill=255)
            fallback_mask = fallback_mask.filter(ImageFilter.GaussianBlur(radius=3))
            fallback_mask.save(mask_path)
            return mask_path
        except Exception as ex:
            logger.error(f"兜底遮罩生成失败: {ex}")
            return mask_path


async def generate_inpaint_tryon(
    outfit_id: str,
    items: list[dict[str, Any]],
    model_id: str = "custom",
    scene: str = "daily",
    target_style: str = "casual",
    user_id: Optional[str] = None,
) -> dict[str, Any]:
    """
    基于通义万相 2.1 局部重绘 (wanx2.1-imageedit + description_edit_with_mask) 的原貌定格换装：
    - 人物不变、动作手势不变、背景不变、头型发型完全不变！
    - 仅重绘被遮罩的衣服区域，实现 100% 真实原貌换装。
    """
    api_key = settings.AI_API_KEY
    if not api_key:
        return _error_result(outfit_id, model_id, "未配置 AI_API_KEY")

    # 1. 寻找模特底图
    model_cfg = _get_model_config(model_id, user_id)
    local_p = Path(model_cfg.get("local_file", ""))
    if not local_p.exists():
        alt_p = Path("apps/api") / model_cfg.get("local_file", "")
        if alt_p.exists():
            local_p = alt_p

    if not local_p.exists():
        logger.warning(f"模特底图不存在: {local_p}，回退至纯白写真生图...")
        return await generate_qwen_fashion_lookbook(
            outfit_id=outfit_id,
            items=items,
            model_id=model_id,
            scene=scene,
            target_style=target_style,
            user_id=user_id,
        )

    # 2. 检查缓存
    cache_dir = Path("uploads") / "tryon"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_filename = f"outfit_{outfit_id}_{model_id}_{user_id}_inpaint_v1.png"
    local_filepath = cache_dir / cache_filename
    local_url = f"/uploads/tryon/{cache_filename}"

    if local_filepath.exists() and local_filepath.stat().st_size > 5000:
        logger.info(f"读取局部重绘换衣缓存: {local_url}")
        return {
            "outfit_id": outfit_id,
            "image_url": local_url,
            "model_id": model_id,
            "source": "wanx2.1-imageedit",
            "engine": "inpaint",
            "prompt": "局部重绘一键定格换装（原貌发型背景100%保留）",
        }

    # 3. 获取或自动生成衣服 Mask
    loop = asyncio.get_running_loop()
    mask_path = await loop.run_in_executor(None, get_or_create_clothing_mask, local_p)
    if not mask_path.exists():
        logger.warning("未能生成服装遮罩，回退至纯白写真生图...")
        return await generate_qwen_fashion_lookbook(
            outfit_id=outfit_id,
            items=items,
            model_id=model_id,
            scene=scene,
            target_style=target_style,
            user_id=user_id,
        )

    # 4. 构建重绘提示词
    color_zh_map = {
        "white": "纯白", "black": "深黑", "blue": "深蓝", "navy": "藏蓝",
        "grey": "浅灰", "gray": "经典灰", "beige": "米白", "brown": "深棕",
        "green": "墨绿", "red": "酒红", "pink": "浅粉", "yellow": "姜黄",
        "khaki": "卡其", "denim": "水洗牛仔", "cream": "奶油白",
    }
    garment_parts = []
    for item in items:
        name = item.get("name", "")
        cat = item.get("category", "")
        color = item.get("color", "") or item.get("primary_color", "")
        zh_color = color_zh_map.get(str(color).lower(), color) if color else ""
        if name:
            if zh_color and zh_color not in name:
                garment_parts.append(f"{zh_color}色{name}")
            else:
                garment_parts.append(name)
        elif cat:
            garment_parts.append(f"{zh_color}色{cat}")

    gender_zh = "男士" if model_cfg.get("gender") == "male" else "女士"
    garments_desc = "，搭配".join(garment_parts) if garment_parts else "一套时尚合身的高级服装"
    inpaint_prompt = (
        f"{gender_zh}身穿{garments_desc}，剪裁利落合身，完美贴合身材体态，"
        f"经典微敞翻领或舒适圆领，领口线条自然平服，自然露出原生修长脖颈线条与喉结，领口与颈部肌肤自然贴合无缝衔接，"
        f"真实高级面料质感与光泽，自然的布料褶皱与环境光影，严禁修改{gender_zh}面部、五官、眼镜、发型、发色、肤色、喉结、手部动作与背景"
    )

    # 5. 图片与蒙版转 Base64
    import base64
    base_b64 = "data:image/jpeg;base64," + base64.b64encode(local_p.read_bytes()).decode("utf-8")
    mask_b64 = "data:image/png;base64," + base64.b64encode(mask_path.read_bytes()).decode("utf-8")

    payload = {
        "model": "wanx2.1-imageedit",
        "input": {
            "function": "description_edit_with_mask",
            "base_image_url": base_b64,
            "mask_image_url": mask_b64,
            "prompt": inpaint_prompt,
        },
        "parameters": {
            "n": 1,
        }
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            submit_resp = await client.post(
                DASHSCOPE_SYNTHESIS_URL,
                headers=headers,
                json=payload,
            )
            if submit_resp.status_code != 200:
                logger.warning(
                    f"wanx2.1-imageedit 提交失败 (HTTP {submit_resp.status_code}): {submit_resp.text}，"
                    "自动回退至纯白写真生图..."
                )
                return await generate_qwen_fashion_lookbook(
                    outfit_id=outfit_id,
                    items=items,
                    model_id=model_id,
                    scene=scene,
                    target_style=target_style,
                    user_id=user_id,
                )

            task_id = submit_resp.json().get("output", {}).get("task_id")
            if not task_id:
                logger.warning("未能获取 imageedit task_id，回退至纯白写真生图...")
                return await generate_qwen_fashion_lookbook(
                    outfit_id=outfit_id,
                    items=items,
                    model_id=model_id,
                    scene=scene,
                    target_style=target_style,
                    user_id=user_id,
                )

            logger.info(f"wanx2.1-imageedit 局部重绘定格换装任务已提交: task_id={task_id}")
            poll_headers = {"Authorization": f"Bearer {api_key}"}
            generated_img_url: Optional[str] = None

            for _ in range(30):
                await asyncio.sleep(2.5)
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
                    if results:
                        generated_img_url = results[0].get("url")
                    break
                elif task_status in ("FAILED", "CANCELED"):
                    logger.warning("wanx2.1-imageedit 任务失败，回退至纯白写真生图...")
                    return await generate_qwen_fashion_lookbook(
                        outfit_id=outfit_id,
                        items=items,
                        model_id=model_id,
                        scene=scene,
                        target_style=target_style,
                        user_id=user_id,
                    )

            if generated_img_url:
                dl_resp = await client.get(generated_img_url, timeout=30.0)
                if dl_resp.status_code == 200:
                    local_filepath.write_bytes(dl_resp.content)
                    logger.info(f"局部重绘一键换衣已成功保存至: {local_url}")
                    return {
                        "outfit_id": outfit_id,
                        "image_url": local_url,
                        "model_id": model_id,
                        "source": "wanx2.1-imageedit",
                        "engine": "inpaint",
                        "prompt": inpaint_prompt,
                    }

    except Exception as e:
        logger.warning(f"局部重绘换衣执行异常: {e}，自动回退至万相生图...")
        return await generate_qwen_fashion_lookbook(
            outfit_id=outfit_id,
            items=items,
            model_id=model_id,
            scene=scene,
            target_style=target_style,
            user_id=user_id,
        )

    return _error_result(outfit_id, model_id, "换装生成超时，请稍后重试")


# ── 综合统一调度接口 ────────────────────────────────────────────────────────
async def generate_tryon_image(
    outfit_id: str,
    items: list[dict[str, Any]],
    gender: str = "unisex",
    scene: str = "daily",
    target_style: str = "casual",
    model_id: str = "female_1",
    engine: str = "inpaint",
    user_id: Optional[str] = None,
) -> dict[str, Any]:
    """
    生图/试衣统一入口。
    - engine="inpaint": 通义万相 2.1 局部重绘定格换装（默认推荐，人物动作姿态、背景、头型发型100%保留）
    - engine="qwen": 阿里通义万相 2.1 旗舰纯白影棚写真（高颜值、纯白空白影棚大片）
    - engine="aitryon": 阿里百炼 OutfitAnyone Plus 1:1 像素级虚拟试穿（支持自动无缝降级）
    - model_id="custom": 用户专属个人形象
    """
    if gender == "male" and model_id == "female_1":
        model_id = "male_1"

    if model_id == "custom" or engine == "inpaint":
        result = await generate_inpaint_tryon(
            outfit_id=outfit_id,
            items=items,
            model_id=model_id,
            scene=scene,
            target_style=target_style,
            user_id=user_id,
        )
    elif engine == "aitryon":
        result = await generate_virtual_tryon(
            outfit_id=outfit_id,
            items=items,
            model_id=model_id,
            scene=scene,
            target_style=target_style,
            user_id=user_id,
        )
    else:
        result = await generate_qwen_fashion_lookbook(
            outfit_id=outfit_id,
            items=items,
            model_id=model_id,
            scene=scene,
            target_style=target_style,
            user_id=user_id,
        )

    result.setdefault("prompt", f"{engine} fashion generation")
    return result
