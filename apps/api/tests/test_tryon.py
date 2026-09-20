"""AI 试穿生图服务测试。"""
import pytest
from unittest.mock import patch


def test_tryon_endpoint(client):
    """测试 /api/v1/recommendations/try-on 端点结构与请求处理。"""
    payload = {
        "outfit_id": "test-outfit-123",
        "items": [
            {
                "sub_category": "连帽卫衣",
                "primary_color": "灰色",
                "image_url": "/uploads/clothing/test.jpg"
            },
            {
                "sub_category": "休闲裤",
                "primary_color": "卡其色",
                "image_url": "/uploads/clothing/test2.jpg"
            }
        ],
        "gender": "male",
        "scene": "daily",
        "target_style": "casual"
    }

    # 使用 mock 避免每次自动化测试均消耗真实生图 API Token
    with patch("app.api.v1.endpoints.recommendations.generate_tryon_image") as mock_gen:
        mock_gen.return_value = {
            "outfit_id": "test-outfit-123",
            "image_url": "/uploads/tryon/test-outfit-123.png",
            "prompt": "Test fashion prompt",
            "source": "wanx"
        }

        response = client.post("/api/v1/recommendations/try-on", json=payload)
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        data = res["data"]
        assert data["outfit_id"] == "test-outfit-123"
        assert "/uploads/tryon/" in data["image_url"]
        assert data["source"] == "wanx"
