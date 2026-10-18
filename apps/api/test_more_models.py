import requests
import json
import os

api_key = ""
with open("D:/AI-Dress/.env", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("AI_API_KEY="):
            api_key = line.strip().split("=", 1)[1]

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "X-DashScope-Async": "enable",
}

# 1. 尝试 Wanx 2.1 图生图 (image2image)
test_candidates = [
    # wanx 图生图系列
    ("https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis", "wanx2.1-i2i-plus", {
        "model": "wanx2.1-i2i-plus",
        "input": {
            "prompt": "person in white t-shirt",
            "base_image_url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250626/ubznva/model_person.png"
        }
    }),
    ("https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis", "wanx2.1-i2i-turbo", {
        "model": "wanx2.1-i2i-turbo",
        "input": {
            "prompt": "person in white t-shirt",
            "base_image_url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250626/ubznva/model_person.png"
        }
    }),
    ("https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis", "wanx-v1", {
        "model": "wanx-v1",
        "input": {
            "prompt": "person in white t-shirt",
            "base_image_url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250626/ubznva/model_person.png"
        }
    }),
    # facechain / 人脸保持
    ("https://dashscope.aliyuncs.com/api/v1/services/aigc/image-generation/generation", "facechain-facedetect", {
        "model": "facechain-facedetect",
        "input": {"image_url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250626/ubznva/model_person.png"}
    }),
    # 通义万相人像风格重绘
    ("https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis", "wanx-sketch-to-image-lite", {
        "model": "wanx-sketch-to-image-lite",
        "input": {"prompt": "person", "sketch_image_url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250626/ubznva/model_person.png"}
    }),
]

for url, model_name, payload in test_candidates:
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"{model_name}: {r.status_code} -> {r.text[:150]}")
    except Exception as e:
        print(f"{model_name}: error {e}")
