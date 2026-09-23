"""
衣橱数据大屏与洞察分析 API 测试。
"""


def test_empty_wardrobe_analytics(client):
    """测试新注册账号（空衣橱）的数据分析返回优雅兜底值"""
    # 注册新用户
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "empty_wardrobe_user", "email": "empty_ana@ex.com", "password": "password123"},
    )
    token = reg.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/analytics/overview", headers=headers)
    assert res.status_code == 200
    data = res.json()["data"]

    # 验证指标与空状态
    assert data["metrics"]["total_items"] == 0
    assert data["metrics"]["capsule_score"] == 0
    assert data["metrics"]["capsule_level"] == "空置待建"
    assert len(data["categories"]) == 0
    assert len(data["versatile_items"]) == 0
    assert "尚未添加任何服饰" in data["diagnosis"]["summary"]


def test_populated_wardrobe_analytics(client):
    """测试包含单品与搭配时的全景分析大包返回"""
    # 注册用户
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "sample_ana_user", "email": "sample_ana@ex.com", "password": "password123"},
    )
    token = reg.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. 导入示例单品 (14件)
    import_res = client.post("/api/v1/clothing/import-samples", headers=headers)
    assert import_res.status_code == 200
    assert import_res.json()["data"]["count"] == 14

    # 2. 获取单品并创建一套收藏搭配
    clothes_res = client.get("/api/v1/clothing/", headers=headers)
    items = clothes_res.json()["data"]["items"]
    sample_ids = [items[0]["id"], items[1]["id"]]

    outfit_res = client.post(
        "/api/v1/outfits",
        json={"name": "秋季舒适出行", "occasion": "casual", "season": "autumn", "item_ids": sample_ids, "overall_score": 90.0},
        headers=headers,
    )
    assert outfit_res.status_code == 200

    # 3. 请求分析接口
    ana_res = client.get("/api/v1/analytics/overview", headers=headers)
    assert ana_res.status_code == 200
    data = ana_res.json()["data"]

    metrics = data["metrics"]
    assert metrics["total_items"] == 14
    assert metrics["total_outfits"] == 1
    assert metrics["capsule_score"] >= 70
    assert metrics["utilization_rate"] > 0

    # 检查品类分布
    categories = data["categories"]
    assert len(categories) == 4
    top_cat = next((c for c in categories if c["key"] == "top"), None)
    assert top_cat is not None
    assert top_cat["count"] > 0

    # 检查百搭单品与闲置清单
    assert len(data["versatile_items"]) > 0
    assert len(data["idle_items"]) > 0

    # 检查色彩分布与中性色比例
    assert data["neutral_ratio"] > 0
    assert len(data["colors"]) > 0

    # 检查诊断报告
    diagnosis = data["diagnosis"]
    assert len(diagnosis["strengths"]) > 0
    assert len(diagnosis["purchase_suggestions"]) > 0


def test_analytics_user_isolation(client):
    """测试不同用户的数据分析完全隔离"""
    # 用户 1
    reg1 = client.post(
        "/api/v1/auth/register",
        json={"username": "iso_user_1", "email": "iso1@ex.com", "password": "password123"},
    )
    token1 = reg1.json()["data"]["access_token"]
    # 导入 14 件
    client.post("/api/v1/clothing/import-samples", headers={"Authorization": f"Bearer {token1}"})

    # 用户 2
    reg2 = client.post(
        "/api/v1/auth/register",
        json={"username": "iso_user_2", "email": "iso2@ex.com", "password": "password123"},
    )
    token2 = reg2.json()["data"]["access_token"]

    # 用户 2 的衣橱应当是 0 件，不被用户 1 影响
    ana2 = client.get("/api/v1/analytics/overview", headers={"Authorization": f"Bearer {token2}"})
    assert ana2.json()["data"]["metrics"]["total_items"] == 0
