"""
多维度评分与推荐理由生成器。
包含：气象评分、风格匹配、场景匹配、色彩协调度以及个性化理由生成。
"""
from typing import Any
from app.services.recommendation.filters import _get_val

# 中性百搭色池
NEUTRAL_COLORS = {"black", "white", "gray", "beige", "navy", "khaki", "黑色", "白色", "灰色", "米色", "藏青", "卡其"}

# 风格相容度映射（相近风格兼容，冲突风格扣分）
STYLE_SIMILARITY: dict[str, dict[str, float]] = {
    "casual": {"casual": 1.0, "minimal": 0.8, "street": 0.8, "sporty": 0.7, "vintage": 0.6, "formal": 0.2},
    "formal": {"formal": 1.0, "elegant": 0.85, "minimal": 0.8, "casual": 0.3, "sporty": 0.1, "street": 0.1},
    "sporty": {"sporty": 1.0, "casual": 0.8, "street": 0.75, "minimal": 0.6, "formal": 0.1, "vintage": 0.3},
    "minimal": {"minimal": 1.0, "casual": 0.85, "formal": 0.8, "elegant": 0.8, "sporty": 0.6, "vintage": 0.6},
    "vintage": {"vintage": 1.0, "casual": 0.75, "elegant": 0.75, "minimal": 0.65, "street": 0.6, "formal": 0.4},
    "street": {"street": 1.0, "casual": 0.85, "sporty": 0.8, "vintage": 0.65, "minimal": 0.5, "formal": 0.1},
    "elegant": {"elegant": 1.0, "formal": 0.85, "minimal": 0.8, "casual": 0.6, "vintage": 0.7, "sporty": 0.2},
}

# 场景推荐风格偏好
SCENE_PREFERENCES: dict[str, dict[str, float]] = {
    "work": {"formal": 1.0, "minimal": 0.9, "elegant": 0.85, "casual": 0.5, "street": 0.2, "sporty": 0.1},
    "interview": {"formal": 1.0, "minimal": 0.9, "elegant": 0.85, "casual": 0.3, "street": 0.1, "sporty": 0.1},
    "daily": {"casual": 1.0, "minimal": 0.95, "sporty": 0.85, "street": 0.8, "vintage": 0.75, "formal": 0.4},
    "class": {"casual": 1.0, "minimal": 0.9, "sporty": 0.85, "street": 0.8, "vintage": 0.75, "formal": 0.3},
    "date": {"casual": 0.9, "elegant": 1.0, "minimal": 0.85, "vintage": 0.85, "street": 0.7, "sporty": 0.4},
    "sports": {"sporty": 1.0, "casual": 0.75, "street": 0.6, "minimal": 0.5, "formal": 0.1, "elegant": 0.1},
    "party": {"street": 1.0, "vintage": 0.9, "elegant": 0.9, "casual": 0.7, "formal": 0.6, "sporty": 0.4},
}


# ==========================================
# 保持向后兼容的单点评分函数 (原有测试覆盖)
# ==========================================

def score_weather(current_temp: float, optimal_temp: float) -> float:
    """单个气温偏离度衰减打分，偏离10度衰减至0。"""
    diff = abs(current_temp - optimal_temp)
    score = max(0.0, 1.0 - (diff / 10.0))
    return round(score, 4)


def score_style(item_style: str, target_style: str) -> float:
    """风格匹配基础打分（完全匹配返回 1.0，否则返回 0.0）。"""
    if item_style.lower() == target_style.lower():
        return 1.0
    return 0.0


def score_style_affinity(item_style: str, target_style: str) -> float:
    """风格亲和度打分（包含相近风格兼容加分）。"""
    s1, s2 = item_style.lower(), target_style.lower()
    if s1 == s2:
        return 1.0
    return STYLE_SIMILARITY.get(s2, {}).get(s1, 0.0)


def score_scene(item_scene: str, target_scene: str) -> float:
    """场景契合打分。"""
    if item_scene.lower() == target_scene.lower():
        return 1.0
    return 0.0


def score_color(color1: str, color2: str) -> float:
    """双色搭配启发式规则打分。"""
    c1, c2 = color1.lower(), color2.lower()
    if c1 == c2:
        return 1.0
    if c1 in NEUTRAL_COLORS or c2 in NEUTRAL_COLORS:
        return 0.8
    return 0.5


# ==========================================
# 整套穿搭（组合级）综合评分与分析函数
# ==========================================

def score_outfit_weather(items: list[Any], current_temp: float) -> float:
    """计算整套穿搭对外界气温的综合舒适契合度。"""
    if not items:
        return 0.5
    scores = []
    has_coat = False
    for item in items:
        cat = str(_get_val(item, "category", "")).lower()
        if cat == "coat":
            has_coat = True
        t_min = _get_val(item, "temp_min")
        t_max = _get_val(item, "temp_max")
        if t_min is not None and t_max is not None:
            optimal = (t_min + t_max) / 2.0
            scores.append(score_weather(current_temp, optimal))
        else:
            scores.append(0.8)

    base_score = sum(scores) / len(scores) if scores else 0.8

    # 气温偏低 (<16℃) 时配备外套加分，过高 (>26℃) 还穿外套扣分
    if current_temp < 16.0 and has_coat:
        base_score = min(1.0, base_score + 0.08)
    elif current_temp > 26.0 and has_coat:
        base_score = max(0.2, base_score - 0.25)

    return round(base_score, 4)


def score_outfit_style(items: list[Any], target_style: str) -> float:
    """计算整套穿搭与用户目标风格的契合度及套装风格协调性。"""
    if not items:
        return 0.5
    item_scores = []
    styles = []
    for item in items:
        st = str(_get_val(item, "style", "casual")).lower()
        styles.append(st)
        item_scores.append(score_style_affinity(st, target_style))

    avg_style = sum(item_scores) / len(item_scores) if item_scores else 0.5

    # 如果整套单品风格完全统一，给予风格一致性加成
    if len(set(styles)) == 1:
        avg_style = min(1.0, avg_style + 0.08)

    return round(avg_style, 4)


def score_outfit_scene(items: list[Any], target_scene: str) -> float:
    """计算整套穿搭与目标场景（如通勤、上课、运动）的适合度。"""
    if not items:
        return 0.5
    scene_prefs = SCENE_PREFERENCES.get(target_scene.lower(), SCENE_PREFERENCES["daily"])
    scores = []
    for item in items:
        st = str(_get_val(item, "style", "casual")).lower()
        cat = str(_get_val(item, "category", "")).lower()
        sub = str(_get_val(item, "sub_category", "")).lower()

        base = scene_prefs.get(st, 0.6)
        # 针对特定场景的单品微调
        if target_scene in ("work", "interview"):
            if sub in ("blazer", "shirt", "trousers", "西装", "衬衫", "西裤"):
                base = min(1.0, base + 0.15)
            elif sub in ("sweatpants", "sandals", "运动裤", "凉鞋"):
                base = max(0.1, base - 0.3)
        elif target_scene == "sports":
            if cat in ("shoes",) or sub in ("sneakers", "sweatpants", "运动鞋", "运动裤"):
                base = min(1.0, base + 0.15)

        scores.append(base)

    return round(sum(scores) / len(scores), 4)


def score_outfit_color(items: list[Any]) -> float:
    """
    根据经典服装配色美学评估全身色彩搭配：
    1. 经典黑白灰中性色基底（百搭高分）
    2. 全身非中性色数量 <= 1（主色突出，干净利落）
    3. 全身彩色过多（超过2种不同杂色）适度扣分
    """
    if not items:
        return 0.8
    colors = [str(_get_val(item, "primary_color", "")).lower() for item in items if _get_val(item, "primary_color")]
    if not colors:
        return 0.8

    # 统计非中性彩色数量
    colored_hues = set(c for c in colors if c not in NEUTRAL_COLORS)

    if len(colored_hues) == 0:
        # 全中性色极简搭配（如黑白灰、藏青+米色），高级百搭
        return 0.95
    elif len(colored_hues) == 1:
        # 单重点色搭配（中性色 + 1个彩色点缀），视觉聚焦，评分优异
        return 0.92
    elif len(colored_hues) == 2:
        # 双色搭配，若颜色相同或相近得高分，否则中等
        return 0.78
    else:
        # 超过2种彩色，容易显得杂乱，给予扣分
        return 0.55


def generate_recommendation_reason(
    items: list[Any],
    current_temp: float,
    target_scene: str,
    target_style: str,
    weather_score: float,
    style_score: float,
    scene_score: float,
    color_score: float
) -> str:
    """生成详实、具有解释性与说服力的穿搭推荐理由。"""
    item_names = []
    item_colors = []
    for it in items:
        sub = _get_val(it, "sub_category") or _get_val(it, "category") or "单品"
        col = _get_val(it, "primary_color", "")
        item_names.append(f"{col}{sub}" if col else str(sub))
        if col:
            item_colors.append(str(col))

    names_str = "、".join(item_names)
    color_str = "搭配".join(list(dict.fromkeys(item_colors))[:3]) or "协调配色"

    reasons = [f"精选组合（{names_str}）。"]

    # 气温点评
    if weather_score >= 0.85:
        reasons.append(f"当前气温约 {current_temp:.0f}℃，整体面料保暖与透气温区极度契合，体感舒适。")
    elif weather_score >= 0.7:
        reasons.append(f"适应约 {current_temp:.0f}℃ 的外界温度，温度适配良好。")
    else:
        reasons.append(f"在 {current_temp:.0f}℃ 环境下具备基础穿着适应度。")

    # 风格与场景点评
    scene_names = {
        "work": "通勤职场", "interview": "求职面试", "daily": "日常休闲",
        "class": "校园上课", "date": "外出约会", "sports": "运动健身", "party": "聚会社交"
    }
    style_names = {
        "casual": "休闲舒适", "formal": "干练正式", "sporty": "活力运动",
        "minimal": "质感极简", "vintage": "经典复古", "street": "潮流街头", "elegant": "优雅气质"
    }
    s_label = style_names.get(target_style.lower(), target_style)
    sc_label = scene_names.get(target_scene.lower(), target_scene)

    reasons.append(f"整体展现【{s_label}】基调，恰当贴合【{sc_label}】氛围要求。")

    # 色彩点评
    if color_score >= 0.9:
        reasons.append(f"全身采用【{color_str}】的经典配色，视觉层次干净和谐。")
    else:
        reasons.append("整体色调搭配平衡耐看。")

    return "".join(reasons)
