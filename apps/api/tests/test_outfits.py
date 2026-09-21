"""
搭配收藏模块测试：收藏、查看列表、多用户隔离与删除。
"""


def test_create_and_list_outfit(client):
    """测试创建搭配收藏并正确查询出包含的单品信息"""
    # 1. 录入一件单品
    item_res = client.post(
        "/api/v1/clothing",
        json={
            "category": "top",
            "sub_category": "tshirt",
            "primary_color": "white",
            "style": "casual",
            "thickness": "thin",
            "season": ["summer"],
            "temp_min": 20.0,
            "temp_max": 32.0,
        },
    )
    item_id = item_res.json()["data"]["id"]

    # 2. 收藏搭配
    outfit_res = client.post(
        "/api/v1/outfits",
        json={
            "name": "夏日清爽白T搭配",
            "occasion": "casual",
            "season": "summer",
            "item_ids": [item_id],
            "overall_score": 92.5,
        },
    )
    assert outfit_res.status_code == 200
    outfit_data = outfit_res.json()["data"]
    assert outfit_data["name"] == "夏日清爽白T搭配"
    assert outfit_data["overall_score"] == 92.5
    assert len(outfit_data["items"]) == 1
    assert outfit_data["items"][0]["primary_color"] == "white"

    # 3. 查列表
    list_res = client.get("/api/v1/outfits")
    assert list_res.status_code == 200
    assert list_res.json()["data"]["total"] >= 1


def test_delete_outfit(client):
    """测试删除搭配收藏"""
    outfit_res = client.post(
        "/api/v1/outfits",
        json={
            "name": "待删除搭配",
            "item_ids": [],
        },
    )
    outfit_id = outfit_res.json()["data"]["id"]

    # 删除
    del_res = client.delete(f"/api/v1/outfits/{outfit_id}")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # 再次删除应 404
    del_again = client.delete(f"/api/v1/outfits/{outfit_id}")
    assert del_again.status_code == 404


def test_outfit_user_isolation(client):
    """测试不同用户的搭配收藏互相隔离且无法越权删除"""
    # 用户 A
    reg_a = client.post(
        "/api/v1/auth/register",
        json={"username": "outfit_user_a", "email": "a_outfit@ex.com", "password": "password123"},
    )
    token_a = reg_a.json()["data"]["access_token"]

    # 用户 B
    reg_b = client.post(
        "/api/v1/auth/register",
        json={"username": "outfit_user_b", "email": "b_outfit@ex.com", "password": "password123"},
    )
    token_b = reg_b.json()["data"]["access_token"]

    # A 收藏一套搭配
    res_a = client.post(
        "/api/v1/outfits",
        json={"name": "A的私服", "item_ids": []},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    outfit_id_a = res_a.json()["data"]["id"]

    # B 查询收藏列表，应该看不到 A 的搭配
    list_b = client.get("/api/v1/outfits", headers={"Authorization": f"Bearer {token_b}"})
    ids_in_b = [o["id"] for o in list_b.json()["data"]["items"]]
    assert outfit_id_a not in ids_in_b

    # B 尝试越权删除 A 的搭配，应当返回 404
    del_b = client.delete(f"/api/v1/outfits/{outfit_id_a}", headers={"Authorization": f"Bearer {token_b}"})
    assert del_b.status_code == 404
