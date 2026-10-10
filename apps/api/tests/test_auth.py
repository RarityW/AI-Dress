"""
用户认证模块测试：注册、登录、Token 验证及权限校验。
"""


def test_register_success(client):
    """测试用户成功注册并获取 JWT Token"""
    res = client.post(
        "/api/v1/auth/register",
        json={
            "username": "test_user_1",
            "email": "user1@example.com",
            "password": "Password123!",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"


def test_register_duplicate_username(client):
    """测试重复用户名注册被拒绝"""
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "dup_user",
            "email": "dup1@example.com",
            "password": "Password123!",
        },
    )
    res = client.post(
        "/api/v1/auth/register",
        json={
            "username": "dup_user",
            "email": "dup2@example.com",
            "password": "Password123!",
        },
    )
    assert res.status_code == 400
    assert "已存在" in res.json()["message"]


def test_register_duplicate_email(client):
    """测试重复邮箱注册被拒绝"""
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "email_user_1",
            "email": "same@example.com",
            "password": "Password123!",
        },
    )
    res = client.post(
        "/api/v1/auth/register",
        json={
            "username": "email_user_2",
            "email": "same@example.com",
            "password": "Password123!",
        },
    )
    assert res.status_code == 400
    assert "已被注册" in res.json()["message"]


def test_login_success(client):
    """测试正确账号密码登录成功"""
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "login_user",
            "email": "login@example.com",
            "password": "CorrectPassword",
        },
    )
    res = client.post(
        "/api/v1/auth/login",
        json={"username": "login_user", "password": "CorrectPassword"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "access_token" in data["data"]


def test_login_with_email_success(client):
    """测试使用注册邮箱登录成功"""
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "email_login_user",
            "email": "mylogin@example.com",
            "password": "CorrectPassword",
        },
    )
    res = client.post(
        "/api/v1/auth/login",
        json={"username": "mylogin@example.com", "password": "CorrectPassword"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "access_token" in data["data"]


def test_login_invalid_password(client):
    """测试密码错误返回 401"""
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "wrong_pwd_user",
            "email": "wrong@example.com",
            "password": "RealPassword",
        },
    )
    res = client.post(
        "/api/v1/auth/login",
        json={"username": "wrong_pwd_user", "password": "WrongPassword"},
    )
    assert res.status_code == 401
    assert res.json()["success"] is False


def test_login_nonexistent_user(client):
    """测试不存在的用户登录返回 401"""
    res = client.post(
        "/api/v1/auth/login",
        json={"username": "no_such_user_xyz", "password": "any"},
    )
    assert res.status_code == 401


def test_get_me_success(client):
    """测试携带 Token 获取当前用户信息"""
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "username": "me_user",
            "email": "me@example.com",
            "password": "Password123",
        },
    )
    token = reg.json()["data"]["access_token"]

    res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["username"] == "me_user"
    assert data["email"] == "me@example.com"
    assert "id" in data


def test_get_me_unauthorized(client):
    """测试未携带 Token 请求 me 接口返回 401"""
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401


def test_account_password_binding_and_username_decoupled(client):
    """测试账号与密码强关联，而用户名仅用作展示昵称，不可作为登录账号"""
    # 1. 注册：账号为 acc_vip_888，展示用户名为 "Zhenqi Fashion VIP"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "account": "acc_vip_888",
            "username": "Zhenqi Fashion VIP",
            "email": "vip@fashion.ai",
            "password": "VipPassword123!",
        },
    )
    assert reg.status_code == 200
    assert reg.json()["success"] is True

    # 2. 尝试使用【用户名 / 昵称】登录 -> 必须被拒绝（401 Unauthorized）
    login_fail = client.post(
        "/api/v1/auth/login",
        json={
            "account": "Zhenqi Fashion VIP",
            "password": "VipPassword123!",
        },
    )
    assert login_fail.status_code == 401
    assert "账号或密码错误" in login_fail.json()["message"]

    # 3. 使用绑定的专属【账号 account】登录 -> 登录成功
    login_ok = client.post(
        "/api/v1/auth/login",
        json={
            "account": "acc_vip_888",
            "password": "VipPassword123!",
        },
    )
    assert login_ok.status_code == 200
    token = login_ok.json()["data"]["access_token"]

    # 4. 获取个人信息：检查 account 与 username 分离正确
    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 200
    me_data = me.json()["data"]
    assert me_data["account"] == "acc_vip_888"
    assert me_data["username"] == "Zhenqi Fashion VIP"

