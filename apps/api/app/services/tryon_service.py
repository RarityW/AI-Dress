"""
AI 试穿与穿搭可视化生图服务 (AI Try-On & Lookbook Synthesis Service)。
对接阿里云通义万相 (DashScope Wanx) 图像生成大模型，根据推荐搭配单品智能构建
全身时尚 Lookbook 摄影级 Prompt，并异步拉取生成整套穿搭模特上身效果图。
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


def build_outfit_prompt(
    items: list[dict[str, Any]],
    gender: str = "unisex",
    scene: str = "daily",
    target_style: str = "casual"
) -> tuple[str, str]:
    """生成精准的全身站姿穿搭正面 Lookbook Prompt 与 Negative Prompt。"""
    pieces_desc = []
    for item in items:
        color = item.get("primary_color", "")
        cat = item.get("category", "")
        sub_cat = item.get("sub_category", "")

        if cat == "top":
            pieces_desc.append(f"上身穿{color}{sub_cat}")
        elif cat == "bottom":
            pieces_desc.append(f"下身穿{color}{sub_cat}")
        elif cat == "coat":
            pieces_desc.append(f"外穿{color}{sub_cat}")
        elif cat == "shoes":
            pieces_desc.append(f"脚穿{color}{sub_cat}")
        else:
            pieces_desc.append(f"{color}{sub_cat}")

    outfit_text = "，".join(pieces_desc)

    gender_desc = {
        "female": "一位年轻东亚女性时尚模特（清秀五官，身材高挑纤细）",
        "male": "一位年轻东亚男性时尚模特（阳光干练，身材匀称挺拔）",
        "unisex": "一位年轻清秀的东亚时尚模特（身材匀称挺拔）"
    }.get(gender, "一位年轻东亚时尚模特（身材匀称挺拔）")

    scene_bg = {
        "daily": "极简纯色现代街区与柔和自然漫射光背景",
        "work": "高级商务写字楼明亮大堂玻璃幕墙背景",
        "date": "浪漫雅致咖啡馆户外阳光街景背景",
        "class": "阳光斑驳的现代大学校园林荫道背景",
        "sports": "开阔极简现代运动场馆浅色背景",
        "party": "现代都市时尚酒廊典雅微光背景"
    }.get(scene, "极简高级摄影棚纯色浅灰背景")

    style_name = {
        "casual": "休闲舒适",
        "formal": "干练正式",
        "sporty": "活力运动",
        "minimal": "质感极简",
        "vintage": "经典复古",
        "elegant": "优雅气质",
        "street": "潮流街头"
    }.get(target_style, "优雅时尚")

    prompt = (
        f"全景全身站姿穿搭时尚Lookbook大片（从头顶到脚底鞋子必须全部完整入镜，全身站立，全身照）。"
        f"{gender_desc}正面站立在镜头正中。"
        f"模特全身清晰穿着整套搭配：{outfit_text}。"
        f"全身搭配风格为【{style_name}】，面料真实褶皱与立体服装剪裁清晰可见，鞋子和裤脚完整露出。"
        f"拍摄场景为{scene_bg}。"
        f"全身构图，正面站姿，高保真单反质感，商业时装画册封面大片，8k超清细节。"
    )

    negative_prompt = (
        "头部特写，面部特写，大头照，半身照，大头贴，胸部以上特写，局部截断，"
        "未拍到裤子，未拍到鞋子，看不到鞋，没穿鞋，大胡子，胡须，络腮胡，白人，欧美面孔，"
        "畸变，多余肢体，肢体残缺，模糊，低画质，全身截断，画框截断"
    )

    return prompt, negative_prompt


async def generate_tryon_image(
    outfit_id: str,
    items: list[dict[str, Any]],
    gender: str = "unisex",
    scene: str = "daily",
    target_style: str = "casual"
) -> dict[str, Any]:
    """
    调用 DashScope Wanx-v1 图像合成 API 生成模特穿搭可视化效果图，
    尺寸严格使用 768*1152 (时尚全身 2:3 构图)，并持久化至 uploads/tryon/。
    """
    save_dir = Path("uploads") / "tryon"
    save_dir.mkdir(parents=True, exist_ok=True)
    local_filename = f"{outfit_id}.png"
    local_filepath = save_dir / local_filename
    local_url = f"/uploads/tryon/{local_filename}"

    # 若本地已有该方案的缓存大片，直接复用
    if local_filepath.exists() and local_filepath.stat().st_size > 5000:
        return {
            "outfit_id": outfit_id,
            "image_url": local_url,
            "prompt": "Cached lookbook synthesis",
            "source": "cache"
        }

    api_key = settings.AI_API_KEY
    prompt, negative_prompt = build_outfit_prompt(
        items,
        gender=gender,
        scene=scene,
        target_style=target_style
    )

    if not api_key:
        logger.warning("未配置 AI_API_KEY，生图跳过")
        return {
            "outfit_id": outfit_id,
            "image_url": "",
            "prompt": prompt,
            "source": "error",
            "error": "未配置 AI_API_KEY，请检查环境变量配置"
        }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }

    # 尺寸必须为官方支持的标准竖版规格: 768*1152 或 720*1280
    payload = {
        "model": "wanx-v1",
        "input": {
            "prompt": prompt,
            "negative_prompt": negative_prompt
        },
        "parameters": {
            "style": "<auto>",
            "size": "768*1152",
            "n": 1
        }
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            submit_resp = await client.post(DASHSCOPE_SYNTHESIS_URL, headers=headers, json=payload)

            if submit_resp.status_code != 200:
                err_msg = f"Wanx 任务提交失败 HTTP {submit_resp.status_code}: {submit_resp.text}"
                logger.error(err_msg)
                return {
                    "outfit_id": outfit_id,
                    "image_url": "",
                    "prompt": prompt,
                    "source": "error",
                    "error": err_msg
                }

            task_id = submit_resp.json().get("output", {}).get("task_id")
            if not task_id:
                err_msg = f"未能获取 task_id: {submit_resp.text}"
                logger.error(err_msg)
                return {
                    "outfit_id": outfit_id,
                    "image_url": "",
                    "prompt": prompt,
                    "source": "error",
                    "error": err_msg
                }

            logger.info(f"Wanx 全身生图任务已提交: task_id={task_id}")

            # 轮询任务状态（最多等待 40 秒）
            max_polls = 16
            poll_headers = {"Authorization": f"Bearer {api_key}"}
            generated_url = None

            for _ in range(max_polls):
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
                        err_detail = data.get("output", {}).get("message", "任务执行失败")
                        logger.error(f"Wanx 任务失败: {err_detail}")
                        return {
                            "outfit_id": outfit_id,
                            "image_url": "",
                            "prompt": prompt,
                            "source": "error",
                            "error": f"通义万相生成失败: {err_detail}"
                        }

            if generated_url:
                dl_resp = await client.get(generated_url, timeout=30.0)
                if dl_resp.status_code == 200:
                    local_filepath.write_bytes(dl_resp.content)
                    logger.info(f"Wanx 全身试穿大片本地持久化成功: {local_url}")
                    return {
                        "outfit_id": outfit_id,
                        "image_url": local_url,
                        "prompt": prompt,
                        "source": "wanx"
                    }

    except Exception as e:
        logger.error(f"AI 生图异常: {e}")
        return {
            "outfit_id": outfit_id,
            "image_url": "",
            "prompt": prompt,
            "source": "error",
            "error": f"生图请求异常: {str(e)}"
        }

    return {
        "outfit_id": outfit_id,
        "image_url": "",
        "prompt": prompt,
        "source": "error",
        "error": "生成超时，请稍后点击重新生成"
    }
