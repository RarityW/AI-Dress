"""
衣橱真实测试数据填充脚本 (Seed Wardrobe Script)。
下载真实高清服装单品图并写入 SQLite 数据库，形成四季全品类可测试的数字衣橱。
"""
import os
import sys
import uuid
from pathlib import Path
import httpx

# 将 apps/api 加入 Python 模块搜索路径并切换工作目录
API_DIR = Path(__file__).resolve().parent.parent / "apps" / "api"
sys.path.insert(0, str(API_DIR))
os.chdir(API_DIR)


from app.core.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.clothing import ClothingItem

ITEMS_DATA = [
    # --- 上装 (Top) ---
    {
        "file_name": "seed_white_tshirt.jpg",
        "url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&q=80",
        "category": "top",
        "sub_category": "短袖T恤",
        "primary_color": "白色",
        "secondary_color": "无",
        "style": "casual",
        "thickness": "thin",
        "season": ["summer", "spring", "autumn"],
        "temp_min": 18.0,
        "temp_max": 36.0,
    },
    {
        "file_name": "seed_grey_hoodie.jpg",
        "url": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=600&q=80",
        "category": "top",
        "sub_category": "连帽卫衣",
        "primary_color": "灰色",
        "secondary_color": "白色",
        "style": "casual",
        "thickness": "medium",
        "season": ["spring", "autumn", "winter"],
        "temp_min": 10.0,
        "temp_max": 22.0,
    },
    {
        "file_name": "seed_blue_shirt.jpg",
        "url": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&q=80",
        "category": "top",
        "sub_category": "长袖衬衫",
        "primary_color": "蓝色",
        "secondary_color": "白色",
        "style": "formal",
        "thickness": "medium",
        "season": ["spring", "autumn", "summer"],
        "temp_min": 15.0,
        "temp_max": 27.0,
    },
    {
        "file_name": "seed_black_sweater.jpg",
        "url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=600&q=80",
        "category": "top",
        "sub_category": "针织毛衣",
        "primary_color": "黑色",
        "secondary_color": "无",
        "style": "vintage",
        "thickness": "thick",
        "season": ["autumn", "winter"],
        "temp_min": 2.0,
        "temp_max": 16.0,
    },

    # --- 下装 (Bottom) ---
    {
        "file_name": "seed_blue_jeans.jpg",
        "url": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=600&q=80",
        "category": "bottom",
        "sub_category": "牛仔裤",
        "primary_color": "蓝色",
        "secondary_color": "无",
        "style": "casual",
        "thickness": "medium",
        "season": ["spring", "summer", "autumn", "winter"],
        "temp_min": 8.0,
        "temp_max": 28.0,
    },
    {
        "file_name": "seed_black_trousers.jpg",
        "url": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=600&q=80",
        "category": "bottom",
        "sub_category": "西装裤",
        "primary_color": "黑色",
        "secondary_color": "无",
        "style": "formal",
        "thickness": "medium",
        "season": ["spring", "autumn", "winter"],
        "temp_min": 10.0,
        "temp_max": 25.0,
    },
    {
        "file_name": "seed_khaki_chinos.jpg",
        "url": "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=600&q=80",
        "category": "bottom",
        "sub_category": "休闲裤",
        "primary_color": "卡其色",
        "secondary_color": "无",
        "style": "casual",
        "thickness": "medium",
        "season": ["spring", "summer", "autumn"],
        "temp_min": 12.0,
        "temp_max": 29.0,
    },

    # --- 外套 (Coat) ---
    {
        "file_name": "seed_trench_coat.jpg",
        "url": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=600&q=80",
        "category": "coat",
        "sub_category": "风衣",
        "primary_color": "卡其色",
        "secondary_color": "黑色",
        "style": "elegant",
        "thickness": "medium",
        "season": ["spring", "autumn"],
        "temp_min": 10.0,
        "temp_max": 20.0,
    },
    {
        "file_name": "seed_black_blazer.jpg",
        "url": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600&q=80",
        "category": "coat",
        "sub_category": "西装外套",
        "primary_color": "黑色",
        "secondary_color": "深灰",
        "style": "formal",
        "thickness": "medium",
        "season": ["spring", "autumn", "winter"],
        "temp_min": 8.0,
        "temp_max": 22.0,
    },
    {
        "file_name": "seed_down_jacket.jpg",
        "url": "https://images.unsplash.com/photo-1548883354-7622d03aca27?w=600&q=80",
        "category": "coat",
        "sub_category": "羽绒服",
        "primary_color": "黑色",
        "secondary_color": "无",
        "style": "casual",
        "thickness": "thick",
        "season": ["winter"],
        "temp_min": -15.0,
        "temp_max": 8.0,
    },

    # --- 鞋履 (Shoes) ---
    {
        "file_name": "seed_white_sneakers.jpg",
        "url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=600&q=80",
        "category": "shoes",
        "sub_category": "板鞋",
        "primary_color": "白色",
        "secondary_color": "灰色",
        "style": "casual",
        "thickness": "medium",
        "season": ["spring", "summer", "autumn", "winter"],
        "temp_min": 5.0,
        "temp_max": 35.0,
    },
    {
        "file_name": "seed_leather_shoes.jpg",
        "url": "https://images.unsplash.com/photo-1614252369475-531eba835eb1?w=600&q=80",
        "category": "shoes",
        "sub_category": "皮鞋",
        "primary_color": "黑色",
        "secondary_color": "棕色",
        "style": "formal",
        "thickness": "medium",
        "season": ["spring", "summer", "autumn", "winter"],
        "temp_min": 5.0,
        "temp_max": 32.0,
    },
    {
        "file_name": "seed_sports_shoes.jpg",
        "url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=80",
        "category": "shoes",
        "sub_category": "运动鞋",
        "primary_color": "红色",
        "secondary_color": "灰色",
        "style": "sporty",
        "thickness": "medium",
        "season": ["spring", "summer", "autumn", "winter"],
        "temp_min": 8.0,
        "temp_max": 35.0,
    },
    {
        "file_name": "seed_boots.jpg",
        "url": "https://images.unsplash.com/photo-1520639888713-7851133b1ed0?w=600&q=80",
        "category": "shoes",
        "sub_category": "靴子",
        "primary_color": "棕色",
        "secondary_color": "黑色",
        "style": "vintage",
        "thickness": "thick",
        "season": ["autumn", "winter"],
        "temp_min": -5.0,
        "temp_max": 18.0,
    },
]


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 获取或创建默认测试用户
        default_user = db.query(User).filter(User.username == "default_user").first()
        if not default_user:
            default_user = User(
                username="default_user",
                email="default@yijian.ai",
                hashed_password="mock-password-hash",
            )
            db.add(default_user)
            db.commit()
            db.refresh(default_user)

        # 确保图片存储目录存在
        upload_dir = Path(__file__).resolve().parent.parent / "apps" / "api" / "uploads" / "clothing"
        upload_dir.mkdir(parents=True, exist_ok=True)

        added_count = 0
        for item_spec in ITEMS_DATA:
            file_name = item_spec["file_name"]
            local_path = upload_dir / file_name

            # 1. 检查是否已经下载，未下载则抓取
            if not local_path.exists() or local_path.stat().st_size < 1000:
                print(f"正在下载图片: {item_spec['sub_category']} ({file_name})...")
                try:
                    resp = httpx.get(item_spec["url"], timeout=15.0)
                    if resp.status_code == 200:
                        local_path.write_bytes(resp.content)
                        print(f"  [OK] 下载完成: {len(resp.content)} 字节")
                    else:
                        print(f"  [WARN] 下载异常 HTTP {resp.status_code}")
                except Exception as e:
                    print(f"  [FAIL] 下载失败: {e}")

            # 2. 检查数据库中是否已存在同款单品
            existing = db.query(ClothingItem).filter(
                ClothingItem.sub_category == item_spec["sub_category"],
                ClothingItem.primary_color == item_spec["primary_color"]
            ).first()

            if not existing:
                clothing_item = ClothingItem(
                    id=uuid.uuid4(),
                    user_id=default_user.id,
                    image_url=f"/uploads/clothing/{file_name}",
                    category=item_spec["category"],
                    sub_category=item_spec["sub_category"],
                    primary_color=item_spec["primary_color"],
                    secondary_color=item_spec["secondary_color"],
                    style=item_spec["style"],
                    thickness=item_spec["thickness"],
                    season=item_spec["season"],
                    temp_min=item_spec["temp_min"],
                    temp_max=item_spec["temp_max"],
                    raw_vlm_attributes={
                        "source": "seed_curated_data",
                        "description": f"精选测试单品：{item_spec['primary_color']}{item_spec['sub_category']}"
                    }
                )
                db.add(clothing_item)
                added_count += 1
                print(f"入库成功: [{item_spec['category']}] {item_spec['primary_color']} {item_spec['sub_category']}")
            else:
                print(f"单品已存在，跳过: {item_spec['primary_color']} {item_spec['sub_category']}")

        db.commit()
        print(f"\n种子数据初始化完成！新入库单品: {added_count} 件，当前数据库单品总数: {db.query(ClothingItem).count()} 件。")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
