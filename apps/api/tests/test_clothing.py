import io
import pytest

def test_upload_image(client):
    # 1x1 pixel PNG bytes
    test_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    
    response = client.post(
        "/api/v1/clothing/upload-image",
        files={"file": ("test.png", io.BytesIO(test_image), "image/png")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "image_url" in data["data"]

def test_create_clothing(client):
    payload = {
        "category": "top",
        "sub_category": "t-shirt",
        "primary_color": "white",
        "style": "casual",
        "thickness": "thin",
        "season": ["summer", "spring"],
        "temp_min": 20.0,
        "temp_max": 35.0,
        "image_url": "/uploads/clothing/test.png"
    }
    
    response = client.post("/api/v1/clothing/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["category"] == "top"
    assert data["data"]["season"] == ["summer", "spring"]
    assert "id" in data["data"]

def test_list_clothing(client):
    payload = {
        "category": "bottom",
        "sub_category": "jeans",
        "primary_color": "blue",
        "style": "casual",
        "thickness": "medium",
        "season": ["spring", "autumn"],
        "temp_min": 10.0,
        "temp_max": 25.0
    }
    
    # Create an item first
    client.post("/api/v1/clothing/", json=payload)
    
    response = client.get("/api/v1/clothing/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total"] >= 1
    assert len(data["data"]["items"]) >= 1

def test_get_clothing_detail(client):
    payload = {
        "category": "coat",
        "sub_category": "jacket",
        "primary_color": "black",
        "style": "formal",
        "thickness": "thick",
        "season": ["winter"],
        "temp_min": -5.0,
        "temp_max": 10.0
    }
    
    create_resp = client.post("/api/v1/clothing/", json=payload)
    item_id = create_resp.json()["data"]["id"]
    
    response = client.get(f"/api/v1/clothing/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == item_id

def test_update_clothing(client):
    payload = {
        "category": "shoes",
        "sub_category": "sneakers",
        "primary_color": "white",
        "style": "sporty",
        "thickness": "medium",
        "season": ["spring", "summer", "autumn", "winter"],
        "temp_min": -10.0,
        "temp_max": 40.0
    }
    
    create_resp = client.post("/api/v1/clothing/", json=payload)
    item_id = create_resp.json()["data"]["id"]
    
    update_payload = {
        "primary_color": "red"
    }
    
    response = client.put(f"/api/v1/clothing/{item_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["primary_color"] == "red"

def test_delete_clothing(client):
    payload = {
        "category": "accessory",
        "sub_category": "hat",
        "primary_color": "black",
        "style": "casual",
        "thickness": "medium",
        "season": ["summer"],
        "temp_min": 20.0,
        "temp_max": 40.0
    }
    
    create_resp = client.post("/api/v1/clothing/", json=payload)
    item_id = create_resp.json()["data"]["id"]
    
    delete_resp = client.delete(f"/api/v1/clothing/{item_id}")
    assert delete_resp.status_code == 200
    
    get_resp = client.get(f"/api/v1/clothing/{item_id}")
    assert get_resp.status_code == 404


def test_clean_and_normalize_vlm_output():
    from app.services.vlm_service import clean_and_normalize_vlm_output

    raw_ai_text = """```json
    {
        "category": "上装",
        "sub_category": "短袖T恤",
        "primary_color": "白色",
        "secondary_color": "黑色",
        "style": "休闲舒适",
        "thickness": "薄",
        "season": ["春", "夏"],
        "temp_min": "20.5",
        "temp_max": "32.0"
    }
    ```"""
    cleaned = clean_and_normalize_vlm_output(raw_ai_text)
    assert cleaned["category"] == "top"
    assert cleaned["style"] == "casual"
    assert cleaned["primary_color"] == "white"
    assert cleaned["secondary_color"] == "black"
    assert cleaned["thickness"] == "thin"
    assert "spring" in cleaned["season"]
    assert "summer" in cleaned["season"]
    assert cleaned["temp_min"] == 20.5
    assert cleaned["temp_max"] == 32.0


def test_vlm_analyze_endpoint(client):
    # 1. 上传图片测试
    test_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    upload_resp = client.post(
        "/api/v1/clothing/upload-image",
        files={"file": ("vlm_test.png", io.BytesIO(test_image), "image/png")}
    )
    assert upload_resp.status_code == 200
    img_url = upload_resp.json()["data"]["image_url"]

    # 2. 调用 /analyze 端点进行智能视觉特征提取
    analyze_resp = client.post(
        "/api/v1/clothing/analyze",
        json={"image_url": img_url}
    )
    assert analyze_resp.status_code == 200
    data = analyze_resp.json()
    assert data["success"] is True
    assert "category" in data["data"]
    assert "sub_category" in data["data"]
    assert "primary_color" in data["data"]
    assert "style" in data["data"]
    assert "thickness" in data["data"]
    assert isinstance(data["data"]["season"], list)
    assert "temp_min" in data["data"]
    assert "temp_max" in data["data"]
