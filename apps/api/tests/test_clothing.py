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
