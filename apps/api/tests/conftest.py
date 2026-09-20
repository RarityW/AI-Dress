"""
pytest 测试公共固件 (fixtures)。
使用内存 SQLite 数据库，避免测试依赖外部文件系统。
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db

# 使用内存数据库，测试结束自动销毁，无需清理文件
SQLALCHEMY_TEST_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # 内存数据库必须用 StaticPool 保持同一连接
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    """在测试会话开始时创建所有表，结束时销毁。"""
    # 必须导入所有模型，让 Base.metadata 注册全部表定义
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    """每个测试函数获得独立的数据库会话，测试结束自动回滚。"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    """TestClient 固件：覆盖 get_db 依赖，使用测试数据库。"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    # 导入 app 放在这里，避免模块加载时触发生产数据库连接
    from app.main import app

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
