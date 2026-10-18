import requests
import json
import time

api_key = ""
with open("D:/AI-Dress/.env", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("AI_API_KEY="):
            api_key = line.strip().split("=", 1)[1]

COLOR_ZH_MAP = {
    "white": "白色", "black": "黑色", "blue": "蓝色", "navy": "藏青色",
    "gray": "灰色", "beige": "米色", "khaki": "卡其色", "brown": "棕色",
    "red": "红色", "green": "绿色", "yellow": "黄色", "pink": "粉色"
}

items = [
    {"category": "top", "sub_category": "纯棉圆领短袖T恤", "primary_color": "white", "material": "高支纯棉"},
    {"category": "bottom", "sub_category": "直筒牛仔裤", "primary_color": "blue", "material": "水洗牛仔"},
    {"category": "shoes", "sub_category": "低帮休闲板鞋", "primary_color": "white", "material": "皮革"}
]

garments = []
for it in items:
    col = COLOR_ZH_MAP.get(it["primary_color"].lower(), it["primary_color"])
    mat = it.get("material", "")
    sub = it.get("sub_category", "")
    garments.append(f"{col}{mat}{sub}".strip())

garments_str = "，".join(garments)

bg_str = "背景：纯白无缝影棚单色背景，高调纯净，纯白色空白背景，完全没有任何背景杂物、无家具、无建筑、无户外街景、无多余道具"
person_str = "真实自然的东亚年轻女性，保持原图自然黑色齐肩直发与自然发际线，严禁改变发型与发色，真实自然的面容神态与细腻皮肤纹理，严格保持真实自然身材与骨骼比例，拒绝夸张头身比，拒绝过分瘦身形变，自然端正站姿"
restriction_str = "画面严格限制：画面中严禁出现任何多余配饰，绝对不要帽子、墨镜、眼镜、项链、耳环、手镯、手表、手提包、单肩包、双肩包，严禁擅自添加清单以外的外套或手持道具。模特仅穿戴指定的搭配服饰，画面干净纯粹"
photo_str = "顶级服装商业画册大片，85mm人像定焦镜头，f/8光圈全身清晰对焦，柔和影棚高调光，8K超清画质"

prompt = f"专业服装模特商业摄影，全身立姿照。{bg_str}。出镜人物：{person_str}。身着服饰搭配：{garments_str}。{restriction_str}。{photo_str}"

print("Prompt:")
print(prompt)
print()

headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "X-DashScope-Async": "enable"}
payload = {"model": "wanx2.1-t2i-plus", "input": {"prompt": prompt}, "parameters": {"size": "1024*1024", "n": 1}}
r = requests.post("https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis", headers=headers, json=payload)
print("Submit:", r.status_code)
task_id = r.json()["output"]["task_id"]
print("Task ID:", task_id)

for i in range(25):
    time.sleep(3)
    resp = requests.get(f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}", headers={"Authorization": f"Bearer {api_key}"})
    data = resp.json()
    status = data.get("output", {}).get("task_status")
    print(f"[{i+1}] {status}")
    if status == "SUCCEEDED":
        url = data["output"]["results"][0]["url"]
        print("SUCCESS:", url)
        img_bytes = requests.get(url).content
        with open("uploads/tryon/test_perfect_white_prompt.png", "wb") as f:
            f.write(img_bytes)
        print("Saved to uploads/tryon/test_perfect_white_prompt.png")
        break
