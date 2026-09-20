"""天气服务接口测试。"""
import pytest


def test_weather_default_city(client):
    """测试默认城市气象获取。"""
    response = client.get("/api/v1/weather")
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    assert "city" in data
    assert "temperature" in data
    assert "condition" in data
    assert isinstance(data["temperature"], (int, float))


def test_weather_specific_city(client):
    """测试知名城市气象获取（如上海）。"""
    response = client.get("/api/v1/weather?city=上海")
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    assert "上海" in data["city"]
    assert isinstance(data["temperature"], (int, float))
    assert data["condition_code"] in ["sunny", "cloudy", "overcast", "rainy", "snowy", "foggy"]


def test_weather_fallback_city(client):
    """测试小众或未映射城市回退保底机制。"""
    response = client.get("/api/v1/weather?city=奇幻森林城")
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    assert data["city"] == "奇幻森林城"
    assert isinstance(data["temperature"], (int, float))
