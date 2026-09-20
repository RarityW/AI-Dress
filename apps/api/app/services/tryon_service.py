"""
AI 试穿与穿搭可视化生图服务 (AI Try-On & Lookbook Synthesis Service)。
对接阿里云通义万相 (DashScope Wanx) 图像生成大模型，根据推荐搭配单品智能构建
高级时尚 Lookbook 摄影 Prompt，并异步拉取生成整套穿搭上身效果图。
"""
import os
import time
import asyncio
import logging
from pathlib import Path
from typing import Any, Optional
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

DASHSCOPE_SYNTHESIS_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
DASHSCOPE_TASK_URL = "https://dashscope.aliyuncs.com/api/v1/tasks"

# 类别中英文映射
CATEGORY_EN_MAP = {
    "短袖T恤": "crewneck t-shirt",
    "长袖T恤": "long-sleeve t-shirt",
    "连帽卫衣": "hooded sweatshirt",
    "圆领卫衣": "crewneck sweatshirt",
    "长袖衬衫": "button-up collared shirt",
    "短袖衬衫": "short-sleeve shirt",
    "针织毛衣": "knit sweater",
    "针织开衫": "knit cardigan",
    "牛仔裤": "classic denim jeans",
    "西装裤": "tailored dress trousers",
    "休闲裤": "casual chino pants",
    "运动裤": "athletic sweatpants",
    "短裤": "tailored shorts",
    "半身裙": "midi skirt",
    "风衣": "classic trench coat",
    "西装外套": "tailored blazer jacket",
    "羽绒服": "puffer winter jacket",
    "夹克": "bomber jacket",
    "毛呢大衣": "wool overcoat",
    "板鞋": "low-top sneakers",
    "运动鞋": "athletic running sneakers",
    "皮鞋": "leather oxford shoes",
    "靴子": "leather ankle boots",
    "帆布鞋": "canvas shoes"
}

COLOR_EN_MAP = {
    "白色": "clean white",
    "黑色": "solid black",
    "灰色": "heather grey",
    "浅灰": "light grey",
    "深灰": "charcoal grey",
    "蓝色": "navy blue",
    "浅蓝": "light blue",
    "深蓝": "deep blue",
    "卡其色": "khaki beige",
    "棕色": "rich brown",
    "米色": "cream beige",
    "红色": "crimson red",
    "绿色": "forest green",
    "黄色": "mustard yellow",
    "粉色": "soft pastel pink"
}


def build_outfit_prompt(
    items: list[dict[str, Any]],
    gender: str = "unisex",
    scene: str = "daily",
    target_style: str = "casual"
) -> str:
    """基于单品清单生成结构化摄影级别英文 Prompt。"""
    pieces_desc = []
    for item in items:
        color_zh = item.get("primary_color", "")
        sub_cat_zh = item.get("sub_category", "")

        color_en = COLOR_EN_MAP.get(color_zh, color_zh)
        sub_cat_en = CATEGORY_EN_MAP.get(sub_cat_zh, sub_cat_zh)
        pieces_desc.append(f"{color_en} {sub_cat_en}")

    joined_pieces = ", ".join(pieces_desc)

    gender_term = "young adult Asian male model" if gender == "male" else (
        "young adult Asian female model" if gender == "female" else "fashionable young Asian model"
    )

    scene_bg = {
        "daily": "minimalist architectural street corner with soft daylight",
        "work": "modern sleek office building lobby with glass and warm ambient light",
        "date": "cozy aesthetic Parisian style outdoor cafe background",
        "class": "sunlit university campus brick building courtyard",
        "sports": "clean minimalist indoor sports complex or outdoor track",
        "party": "chic modern urban lounge with subtle golden bokeh lighting"
    }.get(scene, "clean minimalist editorial photography studio backdrop")

    prompt = (
        f"Full-body high-fashion lookbook photograph of a {gender_term} standing in a relaxed confident pose. "
        f"The model is impeccably styled wearing: {joined_pieces}. "
        f"Style aesthetic: {target_style} chic, elegant silhouette, natural folds and realistic fabric textures. "
        f"Background: {scene_bg}. "
        f"Shot on 85mm f/1.8 lens, sharp focus, cinematic soft lighting, award-winning Vogue editorial lookbook, 8k masterpiece."
    )
    return prompt


async def generate_tryon_image(
    outfit_id: str,
    items: list[dict[str, Any]],
    gender: str = "unisex",
    scene: str = "daily",
    target_style: str = "casual"
) -> dict[str, Any]:
    """
    调用 DashScope Wanx-v1 图像合成 API 生成模特穿搭可视化效果图，
    并自动将生成图片持久化存储至本地 uploads/tryon/ 目录。
    """
    # 确保本地存储目录存在
    save_dir = Path("uploads") / "tryon"
    save_dir.mkdir(parents=True, exist_ok=True)
    local_filename = f"{outfit_id}.png"
    local_filepath = save_dir / local_filename
    local_url = f"/uploads/tryon/{local_filename}"

    # 若已生成过，直接返回已持久化图片
    if local_filepath.exists() and local_filepath.stat().st_size > 5000:
        return {
            "outfit_id": outfit_id,
            "image_url": local_url,
            "prompt": "Cached lookbook synthesis",
            "source": "cache"
        }

    api_key = settings.AI_API_KEY
    prompt = build_outfit_prompt(items, gender=gender, scene=scene, target_style=target_style)

    if not api_key:
        logger.warning("未配置 AI_API_KEY，返回保底预览图")
        # 如果没有配置 key，返回第一件单品图或兜底图
        first_img = items[0].get("image_url", "") if items else ""
        return {
            "outfit_id": outfit_id,
            "image_url": first_img,
            "prompt": prompt,
            "source": "mock"
        }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }

    payload = {
        "model": "wanx-v1",
        "input": {
            "prompt": prompt
        },
        "parameters": {
            "style": "<auto>",
            "size": "768*1024",  # 时尚 3:4 竖构图
            "n": 1
        }
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            submit_resp = await client.post(DASHSCOPE_SYNTHESIS_URL, headers=headers, json=payload)

            if submit_resp.status_code != 200:
                logger.error(f"Wanx 生图任务提交失败 HTTP {submit_resp.status_code}: {submit_resp.text}")
                return {
                    "outfit_id": outfit_id,
                    "image_url": items[0].get("image_url", "") if items else "",
                    "prompt": prompt,
                    "source": "error_fallback"
                }

            task_id = submit_resp.json().get("output", {}).get("task_id")
            if not task_id:
                logger.error(f"未能获取 task_id: {submit_resp.text}")
                return {
                    "outfit_id": outfit_id,
                    "image_url": items[0].get("image_url", "") if items else "",
                    "prompt": prompt,
                    "source": "error_fallback"
                }

            logger.info(f"Wanx 生图任务已提交: task_id={task_id}")

            # 轮询任务状态（最多等待 35 秒）
            max_polls = 14
            poll_headers = {"Authorization": f"Bearer {api_key}"}
            generated_url = None

            for attempt in range(max_polls):
                await asyncio.sleep(2.5)
                poll_resp = await client.get(f"{DASHSCOPE_TASK_URL}/{task_id}", headers=poll_headers)
                if poll_resp.status_code == 200:
                    data = poll_resp.json()
                    status = data.get("output", {}).get("task_status")
                    if status == "SUCCEEDED":
                        results = data.get("output", {}).get("results", [])
                        if results:
                            generated_url = results[0].get("url")
                            break
                    elif status in ["FAILED", "CANCELED"]:
                        logger.error(f"Wanx 任务失败: {data}")
                        break

            if generated_url:
                # 将 OSS 远端图片下载到本地缓存
                dl_resp = await client.get(generated_url, timeout=30.0)
                if dl_resp.status_code == 200:
                    local_filepath.write_bytes(dl_resp.content)
                    logger.info(f"Wanx 生图成功并本地持久化: {local_url}")
                    return {
                        "outfit_id": outfit_id,
                        "image_url": local_url,
                        "prompt": prompt,
                        "source": "wanx"
                    }

    except Exception as e:
        logger.error(f"AI 生图异常: {e}")

    # 兜底回退
    first_img = items[0].get("image_url", "") if items else ""
    return {
        "outfit_id": outfit_id,
        "image_url": first_img,
        "prompt": prompt,
        "source": "fallback"
    }
