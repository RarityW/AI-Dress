"""推荐算法引擎及推荐端点集成测试。"""
import uuid
import pytest
from app.schemas.recommendation import RecommendationRequest
from app.services.recommendation.engine import (
    calculate_overall_score,
    generate_candidate_outfits,
    recommend_outfits
)
from app.services.recommendation.filters import filter_by_temperature, partition_by_category
from app.services.recommendation.scorer import (
    score_weather,
    score_style,
    score_color,
    score_outfit_weather,
    score_outfit_style,
    score_outfit_scene,
    score_outfit_color,
    generate_recommendation_reason
)


def test_calculate_overall_score():
    score = calculate_overall_score(1.0, 1.0, 1.0, 1.0, 1.0)
    assert score == 1.0
    
    score_zero = calculate_overall_score(0.0, 0.0, 0.0, 0.0, 0.0)
    assert score_zero == 0.0


def test_filter_by_temperature():
    items = [
        {"id": 1, "temp_min": 15, "temp_max": 25},
        {"id": 2, "temp_min": 5, "temp_max": 10},
    ]
    filtered = filter_by_temperature(items, 20.0)
    assert len(filtered) == 1
    assert filtered[0]["id"] == 1


def test_score_weather():
    assert score_weather(20.0, 20.0) == 1.0
    assert score_weather(20.0, 30.0) == 0.0


def test_score_style():
    assert score_style("casual", "casual") == 1.0
    assert score_style("formal", "casual") == 0.0


def test_score_color():
    assert score_color("red", "red") == 1.0
    assert score_color("black", "red") == 0.8
    assert score_color("red", "blue") == 0.5


def test_partition_by_category():
    items = [
        {"category": "top", "name": "T-shirt"},
        {"category": "bottom", "name": "Jeans"},
        {"category": "coat", "name": "Jacket"},
        {"category": "shoes", "name": "Sneakers"},
    ]
    parts = partition_by_category(items)
    assert len(parts["top"]) == 1
    assert len(parts["bottom"]) == 1
    assert len(parts["coat"]) == 1
    assert len(parts["shoes"]) == 1


def test_outfit_level_scorers():
    outfit = [
        {"category": "top", "sub_category": "t-shirt", "primary_color": "white", "style": "casual", "temp_min": 18, "temp_max": 28},
        {"category": "bottom", "sub_category": "jeans", "primary_color": "blue", "style": "casual", "temp_min": 15, "temp_max": 25},
    ]
    # 气温评分
    w_score = score_outfit_weather(outfit, 22.0)
    assert 0.8 <= w_score <= 1.0

    # 风格评分
    s_score = score_outfit_style(outfit, "casual")
    assert s_score >= 0.9

    # 场景评分
    sc_score = score_outfit_scene(outfit, "daily")
    assert sc_score >= 0.8

    # 色彩评分 (white中性色 + blue单一彩色)
    c_score = score_outfit_color(outfit)
    assert c_score >= 0.9

    # 推荐理由生成
    reason = generate_recommendation_reason(outfit, 22.0, "daily", "casual", w_score, s_score, sc_score, c_score)
    assert "t-shirt" in reason or "T-shirt" in reason or "white" in reason or "推荐" in reason


def test_recommend_outfits_engine():
    items = [
        {"id": "t1", "category": "top", "sub_category": "t-shirt", "primary_color": "white", "style": "casual", "thickness": "thin", "image_url": "/test.jpg", "temp_min": 18, "temp_max": 28},
        {"id": "t2", "category": "top", "sub_category": "shirt", "primary_color": "blue", "style": "formal", "thickness": "medium", "image_url": "/test2.jpg", "temp_min": 15, "temp_max": 25},
        {"id": "b1", "category": "bottom", "sub_category": "jeans", "primary_color": "black", "style": "casual", "thickness": "medium", "image_url": "/test3.jpg", "temp_min": 15, "temp_max": 26},
        {"id": "s1", "category": "shoes", "sub_category": "sneakers", "primary_color": "white", "style": "casual", "thickness": "medium", "image_url": "/test4.jpg", "temp_min": 10, "temp_max": 30},
    ]
    req = RecommendationRequest(
        city="北京",
        temperature=22.0,
        weather_condition="晴",
        scene="daily",
        target_style="casual",
        top_k=2
    )
    recs = recommend_outfits(items, req)
    assert len(recs) <= 2
    assert len(recs) >= 1
    # 验证排序降序
    if len(recs) > 1:
        assert recs[0].scores.overall_score >= recs[1].scores.overall_score


def test_recommendation_endpoints_integration(client):
    # 1. 预先在测试库中创建几件衣服
    c1 = {
        "category": "top",
        "sub_category": "hoodie",
        "primary_color": "gray",
        "style": "casual",
        "thickness": "medium",
        "season": ["spring", "autumn"],
        "temp_min": 10.0,
        "temp_max": 22.0,
        "image_url": "/uploads/clothing/hoodie.jpg"
    }
    c2 = {
        "category": "bottom",
        "sub_category": "sweatpants",
        "primary_color": "black",
        "style": "casual",
        "thickness": "medium",
        "season": ["spring", "autumn"],
        "temp_min": 10.0,
        "temp_max": 22.0,
        "image_url": "/uploads/clothing/pants.jpg"
    }
    client.post("/api/v1/clothing/", json=c1)
    client.post("/api/v1/clothing/", json=c2)

    # 2. 发起推荐请求
    rec_payload = {
        "city": "北京",
        "temperature": 18.0,
        "weather_condition": "晴",
        "scene": "sports",
        "target_style": "casual",
        "top_k": 3
    }
    resp = client.post("/api/v1/recommendations/", json=rec_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "recommendations" in data["data"]
    assert len(data["data"]["recommendations"]) >= 1

    record_id = data["data"]["record_id"]
    assert record_id is not None

    # 3. 测试查询推荐历史记录
    hist_resp = client.get("/api/v1/recommendations/history")
    assert hist_resp.status_code == 200
    hist_data = hist_resp.json()
    assert hist_data["success"] is True
    assert len(hist_data["data"]) >= 1

    # 4. 测试反馈评价
    feedback_resp = client.post(f"/api/v1/recommendations/{record_id}/feedback", json={"rating": 5})
    assert feedback_resp.status_code == 200
    assert feedback_resp.json()["success"] is True
