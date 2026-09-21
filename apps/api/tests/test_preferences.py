"""
用户偏好设置模块测试：获取、更新、多用户隔离。
"""


def test_get_default_preferences(client):
    """测试获取未配置过的新用户默认偏好"""
    res = client.get("/api/v1/preferences")
    assert res.status_code == 200
    data = res.json()["data"]
    assert "preferred_styles" in data
    assert "avoided_colors" in data
    assert "custom_weights" in data


def test_update_preferences(client):
    """测试更新偏好设置"""
    update_data = {
        "preferred_styles": ["casual", "minimal"],
        "avoided_colors": ["yellow", "pink"],
        "custom_weights": {"weather": 0.4, "style": 0.3, "scene": 0.2, "color": 0.1},
    }
    res = client.put("/api/v1/preferences", json=update_data)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["preferred_styles"] == ["casual", "minimal"]
    assert data["avoided_colors"] == ["yellow", "pink"]
    assert data["custom_weights"]["weather"] == 0.4

    # 再次 GET 校验持久化
    get_res = client.get("/api/v1/preferences")
    assert get_res.json()["data"]["preferred_styles"] == ["casual", "minimal"]


def test_preferences_user_isolation(client):
    """测试不同登录用户的偏好配置相互独立隔离"""
    # 注册用户 A
    reg_a = client.post(
        "/api/v1/auth/register",
        json={"username": "user_a", "email": "a@ex.com", "password": "pass123"},
    )
    token_a = reg_a.json()["data"]["access_token"]

    # 注册用户 B
    reg_b = client.post(
        "/api/v1/auth/register",
        json={"username": "user_b", "email": "b@ex.com", "password": "pass123"},
    )
    token_b = reg_b.json()["data"]["access_token"]

    # A 设置风格为 vintage
    client.put(
        "/api/v1/preferences",
        json={"preferred_styles": ["vintage"]},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    # B 设置风格为 streetwear
    client.put(
        "/api/v1/preferences",
        json={"preferred_styles": ["streetwear"]},
        headers={"Authorization": f"Bearer {token_b}"},
    )

    # 检查 A 的偏好依然是 vintage
    res_a = client.get("/api/v1/preferences", headers={"Authorization": f"Bearer {token_a}"})
    assert res_a.json()["data"]["preferred_styles"] == ["vintage"]

    # 检查 B 的偏好依然是 streetwear
    res_b = client.get("/api/v1/preferences", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b.json()["data"]["preferred_styles"] == ["streetwear"]
