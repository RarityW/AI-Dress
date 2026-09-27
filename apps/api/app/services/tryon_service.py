"""
AI 虚拟试穿服务 (Virtual Try-On Service)。

方案2：双图输入图像级虚拟试穿。
  - 输入1：预设高质量模特底图（人脸永远真实）
  - 输入2：用户衣橱中的真实衣物图片（上衣 / 下装）
  - 模型：阿里云 wanx-virtual-tryon，将衣服智能贴合到模特身上
  - 彻底解决文生图方案中人脸分辨率不足、五官变形的问题

备用模型：wanx-virtual-tryon-v1（Kolors-Virtual-Try-On 同款后端）
"""
import asyncio
import logging
import time
from pathlib import Path
from typing import Any, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── API 端点 ────────────────────────────────────────────────────────────────
# Virtual Try-On 异步提交（POST）
TRYON_SUBMIT_URL = (
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/out-painting"
)
# Virtual Try-On 官方端点（该模型名称走 image2image）
TRYON_V2_URL = (
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis"
)
# 任务查询（GET）
DASHSCOPE_TASK_URL = "https://dashscope.aliyuncs.com/api/v1/tasks"


# ── 预设模特图 ───────────────────────────────────────────────────────────────
# 使用经过版权确认的公开模特图作为底图（Unsplash 等 CC0 授权）
# 人物全身站姿正面，纯色背景，分辨率不低于 768×1024
PRESET_MODELS = [
    {
        "id": "female_1",
        "label": "女性模特 A",
        "gender": "female",
        "thumbnail": "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=400&q=80",
        "full_url": "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=768&q=90",
    },
    {
        "id": "female_2",
        "label": "女性模特 B",
        "gender": "female",
        "thumbnail": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=400&q=80",
        "full_url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=768&q=90",
    },
    {
        "id": "male_1",
        "label": "男性模特 A",
        "gender": "male",
        "thumbnail": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80",
        "full_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=768&q=90",
    },
    {
        "id": "male_2",
        "label": "男性模特 B",
        "gender": "male",
        "thumbnail": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&q=80",
        "full_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=768&q=90",
    },
]


def get_preset_models() -> list[dict[str, str]]:
    """返回预设模特图列表（用于前端选择面板）。"""
    return PRESET_MODELS


def _get_model_url_by_id(model_id: str) -> Optional[str]:
    """根据模特 ID 返回高清底图 URL。"""
    for m in PRESET_MODELS:
        if m["id"] == model_id:
            return m["full_url"]
    return None


async def generate_virtual_tryon(
    outfit_id: str,
    items: list[dict[str, Any]],
    model_id: str = "female_1",
    scene: str = "daily",
    target_style: str = "casual",
) -> dict[str, Any]:
    """
    调用阿里云 wanx-virtual-tryon API 生成虚拟试穿效果图。

    核心流程：
    1. 从 items 中提取上衣/下装的图片 URL
    2. 从预设列表中获取模特底图 URL
    3. 提交异步任务到 wanx-virtual-tryon
    4. 轮询任务状态，最多等待 60 秒
    5. 下载结果图片并持久化到 uploads/tryon/

    Args:
        outfit_id: 方案 UUID，用于缓存命名
        items: 推荐搭配的单品列表（含 category, image_url）
        model_id: 预设模特 ID（见 PRESET_MODELS）
        scene: 场景标识
        target_style: 风格标识

    Returns:
        包含 outfit_id, image_url, source, error 的字典
    """
    save_dir = Path("uploads") / "tryon"
    save_dir.mkdir(parents=True, exist_ok=True)

    # 缓存文件名包含 model_id，不同模特生成不同缓存
    local_filename = f"{outfit_id}_{model_id}.png"
    local_filepath = save_dir / local_filename
    local_url = f"/uploads/tryon/{local_filename}"

    # 如本地已有缓存，直接复用
    if local_filepath.exists() and local_filepath.stat().st_size > 5000:
        logger.info(f"命中试穿缓存: {local_url}")
        return {
            "outfit_id": outfit_id,
            "image_url": local_url,
            "model_id": model_id,
            "source": "cache",
        }

    api_key = settings.AI_API_KEY
    if not api_key:
        return _error_result(outfit_id, model_id, "未配置 AI_API_KEY，请检查环境变量配置")

    # 获取模特底图 URL
    person_image_url = _get_model_url_by_id(model_id)
    if not person_image_url:
        return _error_result(outfit_id, model_id, f"未找到预设模特 ID: {model_id}")

    # 从搭配单品中提取上衣和下装图片 URL
    top_image_url: Optional[str] = None
    bottom_image_url: Optional[str] = None

    for item in items:
        cat = item.get("category", "")
        img = item.get("image_url", "")
        if not img:
            continue
        # 处理相对路径（本地上传图片）
        if img.startswith("/uploads/"):
            img = f"http://127.0.0.1:{_get_server_port()}{img}"
        if cat in ("top", "coat") and not top_image_url:
            top_image_url = img
        elif cat == "bottom" and not bottom_image_url:
            bottom_image_url = img

    # 必须至少有一件可识别的衣物图片
    if not top_image_url and not bottom_image_url:
        logger.warning("搭配中无可识别的衣物图片，降级为展示模特底图")
        return {
            "outfit_id": outfit_id,
            "image_url": person_image_url,
            "model_id": model_id,
            "source": "fallback_no_garment",
        }

    # 若只有上衣或只有下装，允许单件试穿
    logger.info(
        f"发起虚拟试穿: outfit={outfit_id}, model={model_id}, "
        f"top={'有' if top_image_url else '无'}, bottom={'有' if bottom_image_url else '无'}"
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    }

    # wanx-virtual-tryon 请求体
    input_payload: dict[str, Any] = {
        "person_image_url": person_image_url,
    }
    if top_image_url:
        input_payload["top_garment_url"] = top_image_url
    if bottom_image_url:
        input_payload["bottom_garment_url"] = bottom_image_url

    payload = {
        "model": "wanx-virtual-tryon-v1",
        "input": input_payload,
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            # 提交异步任务
            submit_resp = await client.post(
                "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/clothes-segmentation-tryon",
                headers=headers,
                json=payload,
            )

            if submit_resp.status_code not in (200, 202):
                err_body = submit_resp.text
                logger.error(f"Virtual Try-On 任务提交失败 HTTP {submit_resp.status_code}: {err_body}")

                # 如果是权限问题，尝试降级到文本提示模式
                if submit_resp.status_code in (400, 403, 404):
                    logger.warning("wanx-virtual-tryon API 不可用，降级到展示模特底图")
                    return {
                        "outfit_id": outfit_id,
                        "image_url": person_image_url,
                        "model_id": model_id,
                        "source": "fallback_api_unavailable",
                        "error": f"虚拟试穿 API 暂不可用（{submit_resp.status_code}），已显示模特参考图。如需完整试穿效果，请联系管理员开通 wanx-virtual-tryon 权限。",
                    }

                return _error_result(
                    outfit_id, model_id,
                    f"试穿任务提交失败 (HTTP {submit_resp.status_code}): {err_body[:200]}"
                )

            resp_json = submit_resp.json()
            task_id = resp_json.get("output", {}).get("task_id")
            if not task_id:
                return _error_result(outfit_id, model_id, f"未获取到 task_id: {submit_resp.text[:200]}")

            logger.info(f"Virtual Try-On 任务已提交: task_id={task_id}")

            # 轮询任务状态（最多等待 60 秒，每 3 秒查询一次）
            poll_headers = {"Authorization": f"Bearer {api_key}"}
            generated_url: Optional[str] = None

            for poll_idx in range(20):
                await asyncio.sleep(3.0)
                poll_resp = await client.get(
                    f"{DASHSCOPE_TASK_URL}/{task_id}",
                    headers=poll_headers,
                    timeout=10.0,
                )
                if poll_resp.status_code != 200:
                    logger.warning(f"任务查询异常 (第{poll_idx+1}次): HTTP {poll_resp.status_code}")
                    continue

                data = poll_resp.json()
                status = data.get("output", {}).get("task_status", "")
                logger.debug(f"任务状态 (第{poll_idx+1}次): {status}")

                if status == "SUCCEEDED":
                    results = data.get("output", {}).get("results", [])
                    if results:
                        generated_url = results[0].get("url")
                    break
                elif status in ("FAILED", "CANCELED"):
                    err_detail = data.get("output", {}).get("message", "任务执行失败")
                    logger.error(f"Virtual Try-On 任务失败: {err_detail}")
                    return _error_result(outfit_id, model_id, f"试穿生成失败: {err_detail}")

            if generated_url:
                # 下载并本地持久化
                dl_resp = await client.get(generated_url, timeout=30.0)
                if dl_resp.status_code == 200:
                    local_filepath.write_bytes(dl_resp.content)
                    logger.info(f"虚拟试穿图片已保存: {local_url}")
                    return {
                        "outfit_id": outfit_id,
                        "image_url": local_url,
                        "model_id": model_id,
                        "source": "wanx-virtual-tryon",
                    }
                else:
                    return _error_result(outfit_id, model_id, f"结果图下载失败 (HTTP {dl_resp.status_code})")

    except httpx.TimeoutException:
        return _error_result(outfit_id, model_id, "网络请求超时，请稍后重试")
    except Exception as e:
        logger.error(f"Virtual Try-On 异常: {e}", exc_info=True)
        return _error_result(outfit_id, model_id, f"试穿服务异常: {str(e)}")

    return _error_result(outfit_id, model_id, "生成超时（60 秒），请稍后点击重新生成")


def _error_result(outfit_id: str, model_id: str, error: str) -> dict[str, Any]:
    """统一错误返回格式。"""
    return {
        "outfit_id": outfit_id,
        "image_url": "",
        "model_id": model_id,
        "source": "error",
        "error": error,
    }


def _get_server_port() -> int:
    """获取后端服务端口（用于构建本地图片 URL）。"""
    return 8000


# ── 向后兼容：保留旧函数名供遗留代码调用 ──────────────────────────────────────
async def generate_tryon_image(
    outfit_id: str,
    items: list[dict[str, Any]],
    gender: str = "unisex",
    scene: str = "daily",
    target_style: str = "casual",
    model_id: str = "female_1",
) -> dict[str, Any]:
    """
    向后兼容包装函数。新代码请直接调用 generate_virtual_tryon()。
    gender 参数已弃用，改用 model_id 精确指定模特。
    """
    # 根据 gender 自动选择默认模特
    if gender == "male" and model_id == "female_1":
        model_id = "male_1"

    result = await generate_virtual_tryon(
        outfit_id=outfit_id,
        items=items,
        model_id=model_id,
        scene=scene,
        target_style=target_style,
    )

    # 兼容旧 schema（TryOnResponse 需要 prompt 字段）
    result.setdefault("prompt", "wanx-virtual-tryon dual-image mode")
    return result
