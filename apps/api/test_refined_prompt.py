import requests
import json
import time

api_key = ""
with open("D:/AI-Dress/.env", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("AI_API_KEY="):
            api_key = line.strip().split("=", 1)[1]

# 用户专属定制提示词（纯白背景、身材不改、严禁多余饰品、锁定发型）
prompt = (
    "A full-body professional studio fashion lookbook portrait of an authentic East Asian young woman. "
    "Background: completely blank, seamless solid pure white studio cyclorama background, perfectly even high-key lighting, zero clutter, no shadows on background, no background props, no furniture. "
    "Person Appearance & Hairstyle: natural neat straight shoulder-length black hair parted naturally, exact original natural hairstyle preserved, authentic natural East Asian facial features, realistic human skin texture with natural pores, subtle warm natural expression. "
    "Body Shape & Physique: natural everyday human body proportions, realistic authentic body shape matching the user, natural waistline and realistic shoulder width, strictly avoid exaggerated supermodel proportions, realistic natural standing posture. "
    "Outfit: strictly wearing only two items: a clean crisp white premium cotton short-sleeve T-shirt, paired with classic dark blue straight-leg denim jeans, and clean white minimalist sneakers. "
    "Negative & Restrictions: ABSOLUTELY NO extra accessories, NO hats, NO caps, NO sunglasses, NO eyeglasses, NO handbags, NO shoulder bags, NO backpacks, NO watches, NO bracelets, NO necklaces, NO earrings, NO rings, NO scarves, NO jackets, NO handheld items. Only the specified clothing items. "
    "Photography: 85mm portrait prime lens, f/8 aperture for crisp overall focus, 8k uhd, commercial catalog photography."
)

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "X-DashScope-Async": "enable",
}

payload = {
    "model": "wanx2.1-t2i-plus",
    "input": {"prompt": prompt},
    "parameters": {
        "size": "1024*1024",
        "n": 1,
    },
}

print("正在提交万相 2.1 旗舰专业纯净版生图任务...")
r = requests.post("https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis", headers=headers, json=payload)
print(r.status_code, r.text)
task_id = r.json()["output"]["task_id"]
print(f"Task ID: {task_id}，正在轮询结果...")

poll_headers = {"Authorization": f"Bearer {api_key}"}
for i in range(25):
    time.sleep(3)
    resp = requests.get(f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}", headers=poll_headers)
    data = resp.json()
    status = data.get("output", {}).get("task_status")
    print(f"[{i+1}] 状态: {status}")
    if status == "SUCCEEDED":
        img_url = data["output"]["results"][0]["url"]
        print("生成成功！URL:", img_url)
        # 下载图片
        img_data = requests.get(img_url).content
        with open("D:/AI-Dress/uploads/tryon/test_refined_pure_white.png", "wb") as f:
            f.write(img_data)
        print("图片已保存到 D:/AI-Dress/uploads/tryon/test_refined_pure_white.png")
        break
    elif status in ("FAILED", "CANCELED"):
        print("生成失败:", data)
        break
