"""
DashScope 可用模型探测脚本
测试当前 API Key 下可以调用的所有生图/试穿模型
"""
import requests
import json
import os

# 从 .env 文件读取 API Key
api_key = ""
for env_candidate in [
    os.path.join(os.path.dirname(__file__), ".env"),
    os.path.join(os.path.dirname(__file__), "..", "..", ".env"),
    "D:/AI-Dress/.env",
]:
    if os.path.exists(env_candidate):
        with open(env_candidate, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("AI_API_KEY="):
                    api_key = line.strip().split("=", 1)[1]
        if api_key:
            break

if not api_key:
    print("错误：未找到 AI_API_KEY")
    exit(1)

headers_async = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "X-DashScope-Async": "enable",
}
headers_sync = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

T2I_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
I2I_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis"
GEN_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image-generation/generation"

# 官方示例图片
PERSON_URL = "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250626/ubznva/model_person.png"
TOP_URL = "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250626/nwjkrq/top.png"

results = {}

# 1. aitryon-plus 虚拟试穿
print("【1/6】 测试 aitryon-plus 虚拟试穿模型...")
try:
    r = requests.post(I2I_URL, headers=headers_async, json={
        "model": "aitryon-plus",
        "input": {"person_image_url": PERSON_URL, "top_garment_url": TOP_URL},
        "parameters": {"resolution": -1, "restore_face": True}
    }, timeout=15)
    results["aitryon-plus"] = {"status": r.status_code, "response": r.text[:300]}
    print(f"    状态码: {r.status_code}")
    print(f"    响应: {r.text[:200]}")
except Exception as e:
    results["aitryon-plus"] = {"status": "error", "response": str(e)}
    print(f"    错误: {e}")
print()

# 2. wanx2.1-t2i-plus
print("【2/6】 测试 wanx2.1-t2i-plus 万相旗舰文生图模型...")
try:
    r = requests.post(T2I_URL, headers=headers_async, json={
        "model": "wanx2.1-t2i-plus",
        "input": {"prompt": "a person standing, white background, fashion photo"},
        "parameters": {"size": "512*512", "n": 1}
    }, timeout=15)
    results["wanx2.1-t2i-plus"] = {"status": r.status_code, "response": r.text[:300]}
    print(f"    状态码: {r.status_code}")
    print(f"    响应: {r.text[:200]}")
except Exception as e:
    results["wanx2.1-t2i-plus"] = {"status": "error", "response": str(e)}
    print(f"    错误: {e}")
print()

# 3. flux-schnell
print("【3/6】 测试 flux-schnell 高质量文生图模型...")
try:
    r = requests.post(T2I_URL, headers=headers_async, json={
        "model": "flux-schnell",
        "input": {"prompt": "a person standing, white background, fashion photo"},
        "parameters": {"size": "512*512", "n": 1}
    }, timeout=15)
    results["flux-schnell"] = {"status": r.status_code, "response": r.text[:300]}
    print(f"    状态码: {r.status_code}")
    print(f"    响应: {r.text[:200]}")
except Exception as e:
    results["flux-schnell"] = {"status": "error", "response": str(e)}
    print(f"    错误: {e}")
print()

# 4. flux-dev
print("【4/6】 测试 flux-dev 最高质量文生图模型...")
try:
    r = requests.post(T2I_URL, headers=headers_async, json={
        "model": "flux-dev",
        "input": {"prompt": "a person standing, white background, fashion photo"},
        "parameters": {"size": "512*512", "n": 1}
    }, timeout=15)
    results["flux-dev"] = {"status": r.status_code, "response": r.text[:300]}
    print(f"    状态码: {r.status_code}")
    print(f"    响应: {r.text[:200]}")
except Exception as e:
    results["flux-dev"] = {"status": "error", "response": str(e)}
    print(f"    错误: {e}")
print()

# 5. wanx-style-cosplay-v1 (人脸保持)
print("【5/6】 测试 wanx-style-cosplay-v1 人脸保持模型...")
try:
    r = requests.post(GEN_URL, headers=headers_async, json={
        "model": "wanx-style-cosplay-v1",
        "input": {"face_image_url": PERSON_URL, "template_image_url": TOP_URL}
    }, timeout=15)
    results["wanx-style-cosplay-v1"] = {"status": r.status_code, "response": r.text[:300]}
    print(f"    状态码: {r.status_code}")
    print(f"    响应: {r.text[:200]}")
except Exception as e:
    results["wanx-style-cosplay-v1"] = {"status": "error", "response": str(e)}
    print(f"    错误: {e}")
print()

# 6. wanx2.1-t2i-turbo
print("【6/6】 测试 wanx2.1-t2i-turbo 万相极速文生图模型...")
try:
    r = requests.post(T2I_URL, headers=headers_async, json={
        "model": "wanx2.1-t2i-turbo",
        "input": {"prompt": "a person standing, white background, fashion photo"},
        "parameters": {"size": "512*512", "n": 1}
    }, timeout=15)
    results["wanx2.1-t2i-turbo"] = {"status": r.status_code, "response": r.text[:300]}
    print(f"    状态码: {r.status_code}")
    print(f"    响应: {r.text[:200]}")
except Exception as e:
    results["wanx2.1-t2i-turbo"] = {"status": "error", "response": str(e)}
    print(f"    错误: {e}")
print()

# 汇总
print("=" * 60)
print("模型可用性汇总报告")
print("=" * 60)
for model, info in results.items():
    status = info["status"]
    ok = "✅ 可用" if status == 200 else f"❌ 不可用 (HTTP {status})"
    print(f"  {model:30s} -> {ok}")
print("=" * 60)
