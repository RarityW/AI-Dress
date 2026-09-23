"""
衣橱数据分析与洞察服务。
负责聚合用户衣橱的资产结构、品类/色彩/四季分布、
单品百搭度评估、闲置预警以及胶囊衣橱健康度诊断。
"""
from datetime import datetime
from typing import Any
from collections import Counter

from app.models.clothing import ClothingItem
from app.models.outfit import Outfit
from app.schemas.analytics import (
    MetricOverview,
    DistributionItem,
    ColorDistributionItem,
    VersatileItem,
    IdleItem,
    WardrobeDiagnosis,
    AnalyticsOverviewResponse,
)

# 基础色彩 HEX 映射
COLOR_HEX_MAP: dict[str, str] = {
    "白色": "#FFFFFF",
    "黑色": "#1E293B",
    "灰色": "#94A3B8",
    "蓝色": "#3B82F6",
    "深灰": "#475569",
    "卡其色": "#D4A373",
    "棕色": "#8B5E3C",
    "红色": "#EF4444",
    "米色": "#F5F5DC",
    "绿色": "#10B981",
    "黄色": "#F59E0B",
    "粉色": "#EC4899",
    "紫色": "#8B5CF6",
    "藏青": "#1E3A8A",
    "深蓝": "#1E40AF",
}

# 基础中性色集合
NEUTRAL_COLORS = {"白色", "黑色", "灰色", "深灰", "米色", "卡其色", "棕色", "藏青", "深蓝"}

CATEGORY_LABELS = {
    "top": "上装",
    "bottom": "裤装/下装",
    "coat": "外套",
    "shoes": "鞋履",
}

CATEGORY_COLORS = {
    "top": "#6366F1",    # Indigo
    "bottom": "#0EA5E9", # Sky
    "coat": "#F59E0B",   # Amber
    "shoes": "#10B981",  # Emerald
}

SEASON_LABELS = {
    "spring": "春季",
    "summer": "夏季",
    "autumn": "秋季",
    "winter": "冬季",
}

STYLE_LABELS = {
    "casual": "休闲舒适",
    "formal": "干练正式",
    "sporty": "活力运动",
    "street": "潮流街头",
    "vintage": "经典复古",
    "elegant": "优雅气质",
    "minimal": "质感极简",
}


def analyze_wardrobe_overview(
    items: list[ClothingItem],
    outfits: list[Outfit],
) -> AnalyticsOverviewResponse:
    """全面聚合用户衣橱与穿搭收藏，生成综合洞察分析大包。"""
    total_items = len(items)
    total_outfits = len(outfits)

    # 1. 极端空衣橱兜底处理
    if total_items == 0:
        return AnalyticsOverviewResponse(
            metrics=MetricOverview(
                total_items=0,
                total_outfits=total_outfits,
                utilization_rate=0.0,
                capsule_score=0,
                capsule_level="空置待建",
            ),
            categories=[],
            seasons=[],
            styles=[],
            colors=[],
            neutral_ratio=0.0,
            versatile_items=[],
            idle_items=[],
            diagnosis=WardrobeDiagnosis(
                summary="当前衣橱尚未添加任何服饰，资产与结构分析暂不可用。",
                strengths=["衣橱是一张白纸，具备极大的规划自由度。"],
                weaknesses=["缺少基础款服饰支撑，无法进行算法穿搭推荐。"],
                purchase_suggestions=["建议先点击「一键导入体验示例衣橱」或上传您的常用上下装单品。"],
            ),
        )

    # 2. 统计搭配中被引用的单品频次
    used_item_counts: Counter[str] = Counter()
    for outfit in outfits:
        if outfit.item_ids and isinstance(outfit.item_ids, list):
            for i_id in outfit.item_ids:
                used_item_counts[str(i_id)] += 1

    distinct_used_count = len([iid for iid in used_item_counts if any(str(it.id) == iid for it in items)])
    utilization_rate = round((distinct_used_count / total_items) * 100, 1)

    # 3. 品类分布统计
    cat_counter = Counter(it.category for it in items)
    categories_dist: list[DistributionItem] = []
    for cat_key in ["top", "bottom", "coat", "shoes"]:
        cnt = cat_counter.get(cat_key, 0)
        categories_dist.append(
            DistributionItem(
                key=cat_key,
                label=CATEGORY_LABELS.get(cat_key, cat_key),
                count=cnt,
                percentage=round((cnt / total_items) * 100, 1) if total_items > 0 else 0.0,
                color=CATEGORY_COLORS.get(cat_key, "#64748B"),
            )
        )

    # 4. 季节分布统计 (一件衣服可覆盖多个季节)
    season_counter: Counter[str] = Counter()
    for it in items:
        if it.season and isinstance(it.season, list):
            for s in it.season:
                season_counter[s] += 1
        elif isinstance(it.season, dict):
            for s in it.season.keys():
                season_counter[s] += 1

    seasons_dist: list[DistributionItem] = []
    for s_key in ["spring", "summer", "autumn", "winter"]:
        cnt = season_counter.get(s_key, 0)
        seasons_dist.append(
            DistributionItem(
                key=s_key,
                label=SEASON_LABELS.get(s_key, s_key),
                count=cnt,
                percentage=round((cnt / total_items) * 100, 1) if total_items > 0 else 0.0,
                color="#6366F1" if s_key == "spring" else "#10B981" if s_key == "summer" else "#F59E0B" if s_key == "autumn" else "#3B82F6",
            )
        )

    # 5. 风格偏好分布
    style_counter = Counter(it.style for it in items if it.style)
    styles_dist: list[DistributionItem] = []
    for s_key, cnt in style_counter.most_common():
        styles_dist.append(
            DistributionItem(
                key=s_key,
                label=STYLE_LABELS.get(s_key, s_key),
                count=cnt,
                percentage=round((cnt / total_items) * 100, 1),
            )
        )

    # 6. 色彩分布与调色盘
    color_counter = Counter(it.primary_color for it in items if it.primary_color)
    colors_dist: list[ColorDistributionItem] = []
    neutral_count = 0
    for color_name, cnt in color_counter.most_common():
        is_neutral = color_name in NEUTRAL_COLORS
        if is_neutral:
            neutral_count += cnt
        colors_dist.append(
            ColorDistributionItem(
                color_name=color_name,
                hex_code=COLOR_HEX_MAP.get(color_name, "#64748B"),
                count=cnt,
                percentage=round((cnt / total_items) * 100, 1),
                is_neutral=is_neutral,
            )
        )
    neutral_ratio = round((neutral_count / total_items) * 100, 1) if total_items > 0 else 0.0

    # 7. 百搭之星评估 (Versatile Items)
    # 结合被收藏使用次数 + 理论百搭度 (中性色、全季覆盖、经典品类)
    scored_items: list[tuple[ClothingItem, int, float, str]] = []
    for it in items:
        actual_matches = used_item_counts.get(str(it.id), 0)
        # 理论百搭度基础分
        v_score = 65.0
        reasons = []

        if it.primary_color in NEUTRAL_COLORS:
            v_score += 15.0
            reasons.append("经典中性色调")

        if it.season and isinstance(it.season, (list, dict)) and len(it.season) >= 3:
            v_score += 10.0
            reasons.append("跨季高频穿戴")

        if any(keyword in it.sub_category for keyword in ["T恤", "牛仔裤", "衬衫", "板鞋", "风衣", "休闲裤"]):
            v_score += 8.0
            reasons.append("核心百搭廓形")

        if actual_matches > 0:
            v_score += min(12.0, actual_matches * 4.0)
            reasons.append(f"已收录在 {actual_matches} 套心仪穿搭中")

        v_score = min(99.0, max(50.0, round(v_score, 1)))
        highlight = " · ".join(reasons) if reasons else "基础搭配单品"
        scored_items.append((it, actual_matches, v_score, highlight))

    # 按百搭分排序，取 Top 3
    scored_items.sort(key=lambda x: (x[1], x[2]), reverse=True)
    versatile_items: list[VersatileItem] = []
    for it, matches, v_score, highlight in scored_items[:3]:
        versatile_items.append(
            VersatileItem(
                id=str(it.id),
                category=it.category,
                sub_category=it.sub_category,
                primary_color=it.primary_color,
                style=it.style,
                image_url=it.image_url,
                match_count=matches,
                versatility_score=v_score,
                highlight_reason=highlight,
            )
        )

    # 8. 闲置预警清单 (Idle Items)
    # 取 actual_matches == 0 且入库较早或百搭度较低的单品，最多取 4 件
    idle_candidates = [entry for entry in scored_items if entry[1] == 0]
    # 若全部都有搭配，则取使用最少的倒数单品
    if not idle_candidates:
        idle_candidates = sorted(scored_items, key=lambda x: x[1])

    idle_items: list[IdleItem] = []
    now = datetime.now()
    for it, matches, v_score, _ in idle_candidates[:4]:
        days_in = (now - it.created_at).days if it.created_at else 1
        temp_str = f"{int(it.temp_min)}℃ ~ {int(it.temp_max)}℃"

        # 智能唤醒建议
        if it.category == "coat":
            revive_text = f"建议在气温下降到 {int(it.temp_min)}℃ 时搭配浅色打底衫与西装裤激活。"
        elif it.category == "shoes":
            revive_text = f"推荐与日常休闲风格的牛仔裤或休闲裤组合出行。"
        elif it.category == "bottom":
            revive_text = f"可与衣橱中的百搭上装组合，拓宽日常通勤穿着边界。"
        else:
            revive_text = f"适宜在 {temp_str} 温区作为外穿或内搭叠穿。"

        idle_items.append(
            IdleItem(
                id=str(it.id),
                category=it.category,
                sub_category=it.sub_category,
                primary_color=it.primary_color,
                style=it.style,
                image_url=it.image_url,
                temp_range=temp_str,
                idle_days=max(1, days_in),
                revive_suggestion=revive_text,
            )
        )

    # 9. 计算胶囊衣橱健康度 (0 - 100 分)
    capsule_score = 0
    # A. 品类结构完整性 (满分 35 分)
    has_top = cat_counter.get("top", 0) > 0
    has_bottom = cat_counter.get("bottom", 0) > 0
    has_shoes = cat_counter.get("shoes", 0) > 0
    has_coat = cat_counter.get("coat", 0) > 0

    cat_coverage_count = sum([has_top, has_bottom, has_shoes, has_coat])
    capsule_score += cat_coverage_count * 8  # 最多 32 分
    if cat_coverage_count == 4:
        capsule_score += 3  # 满分类别奖励 3 分

    # B. 中性色占比 (满分 25 分): 理想胶囊衣橱中性色在 55% ~ 80% 之间
    if 50 <= neutral_ratio <= 85:
        capsule_score += 25
    elif 30 <= neutral_ratio < 50 or 85 < neutral_ratio <= 95:
        capsule_score += 18
    else:
        capsule_score += 10

    # C. 四季温区覆盖度 (满分 20 分)
    covered_seasons = len([s for s in ["spring", "summer", "autumn", "winter"] if season_counter.get(s, 0) > 0])
    capsule_score += covered_seasons * 5  # 最多 20 分

    # D. 衣橱利用率与单品数 (满分 20 分)
    if total_items >= 10:
        capsule_score += 10
    elif total_items >= 5:
        capsule_score += 6

    if utilization_rate >= 40:
        capsule_score += 10
    elif utilization_rate > 0:
        capsule_score += 6

    capsule_score = min(100, max(20, capsule_score))

    if capsule_score >= 85:
        capsule_level = "黄金胶囊衣橱"
    elif capsule_score >= 70:
        capsule_level = "均衡实用衣橱"
    elif capsule_score >= 50:
        capsule_level = "尚需补全结构"
    else:
        capsule_level = "初建探索阶段"

    # 10. 生成衣橱诊断报告
    strengths: list[str] = []
    weaknesses: list[str] = []
    suggestions: list[str] = []

    if neutral_ratio >= 60:
        strengths.append(f"基础中性色占比高达 {neutral_ratio}%，极易相互混搭，具备良好的极简胶囊衣橱底盘。")
    else:
        strengths.append("色彩丰富活泼，具有鲜明的个性化视觉表现力。")

    if cat_coverage_count == 4:
        strengths.append("品类覆盖完整（上衣、下装、外套、鞋履均有配置），可应对完整闭环搭配需求。")

    if not has_coat:
        weaknesses.append("缺少外套品类（如夹克、风衣或羽绒服），面对大幅度换季降温时搭配容错度偏低。")
        suggestions.append("优先添置 1 件黑色西装外套或经典卡其色风衣，大幅提升防风御寒与层次感。")

    if not has_shoes:
        weaknesses.append("未录入鞋履单品，无法输出端到端的全身闭环搭配方案。")
        suggestions.append("添加 1 双白色休闲板鞋和 1 双皮鞋/靴子，打通完整穿搭链条。")

    top_count = cat_counter.get("top", 0)
    bottom_count = cat_counter.get("bottom", 0)
    if top_count > 0 and bottom_count > 0:
        ratio = round(top_count / bottom_count, 1)
        if ratio > 2.5:
            weaknesses.append(f"上装与下装比例为 {top_count}:{bottom_count}，裤装选择稍显单薄。")
            suggestions.append("增补 1 条深色微锥形长裤或直筒休闲西裤，快速提升下半身轮换率。")

    if not weaknesses:
        weaknesses.append("单品间的搭配深度还可进一步挖掘，部分单品尚未被收录到心仪搭配方案中。")

    if not suggestions:
        suggestions.append("当前衣橱结构非常健康！建议前往「智能推荐」多收藏不同温区场景的搭配，充分激活每件衣服。")

    summary_text = (
        f"您的数字衣橱已收录 {total_items} 件精选单品，胶囊健康度达 {capsule_score} 分（{capsule_level}）。"
        f"基础中性色占比 {neutral_ratio}%，四季整体均衡。遵循「少而精」的搭配哲学，继续保持与优化。"
    )

    diagnosis = WardrobeDiagnosis(
        summary=summary_text,
        strengths=strengths,
        weaknesses=weaknesses,
        purchase_suggestions=suggestions,
    )

    return AnalyticsOverviewResponse(
        metrics=MetricOverview(
            total_items=total_items,
            total_outfits=total_outfits,
            utilization_rate=utilization_rate,
            capsule_score=capsule_score,
            capsule_level=capsule_level,
        ),
        categories=categories_dist,
        seasons=seasons_dist,
        styles=styles_dist,
        colors=colors_dist,
        neutral_ratio=neutral_ratio,
        versatile_items=versatile_items,
        idle_items=idle_items,
        diagnosis=diagnosis,
    )
