"""
自主穿搭推荐决策引擎。
负责：候选穿搭组合生成、多维度综合打分、降序排列与 TOP-K 输出。
"""
import uuid
from typing import Any
from app.core.config import settings
from app.schemas.recommendation import (
    RecommendationRequest,
    OutfitRecommendation,
    OutfitItemDetail,
    ScoreBreakdown
)
from app.services.recommendation.filters import (
    _get_val,
    filter_by_temperature,
    partition_by_category
)
from app.services.recommendation.scorer import (
    score_outfit_weather,
    score_outfit_style,
    score_outfit_scene,
    score_outfit_color,
    generate_recommendation_reason
)


def calculate_overall_score(
    weather_score: float,
    style_score: float,
    scene_score: float,
    color_score: float,
    preference_score: float = 0.8,
    custom_weights: dict[str, float] = None
) -> float:
    """
    多目标加权决策打分公式：
    S = w_weather * S_weather + w_style * S_style + w_scene * S_scene + w_color * S_color + w_pref * S_pref
    支持用户自定义权重，若无则使用系统默认配置。
    """
    w_weather = settings.WEIGHT_WEATHER
    w_style = settings.WEIGHT_STYLE
    w_scene = settings.WEIGHT_SCENE
    w_color = settings.WEIGHT_COLOR
    w_pref = settings.WEIGHT_PREFERENCE

    if custom_weights:
        w_weather = custom_weights.get("weather", w_weather)
        w_style = custom_weights.get("style", w_style)
        w_scene = custom_weights.get("scene", w_scene)
        w_color = custom_weights.get("color", w_color)
        w_pref = custom_weights.get("preference", w_pref)
        total_w = w_weather + w_style + w_scene + w_color + w_pref
        if total_w > 0:
            w_weather /= total_w
            w_style /= total_w
            w_scene /= total_w
            w_color /= total_w
            w_pref /= total_w

    total = (
        w_weather * weather_score +
        w_style * style_score +
        w_scene * scene_score +
        w_color * color_score +
        w_pref * preference_score
    )
    return min(1.0, max(0.0, total))


def generate_candidate_outfits(items: list[Any], current_temp: float) -> list[list[Any]]:
    """
    根据气象温区与衣橱品类，生成穿搭拓扑组合：
    - 基础框架：上装 (Top) + 下装 (Bottom)
    - 气温偏低或有外套时扩展：上装 + 下装 + 外套 (Coat)
    - 可选鞋履配饰补充：+ 鞋履 (Shoes)
    - 当衣物较少时具备自适应降级能力。
    """
    if not items:
        return []

    # 1. 气温适宜度初步过滤
    temp_filtered = filter_by_temperature(items, current_temp, tolerance=4.0)
    # 若过滤后太少，则回退使用全量单品以保障有结果展示
    working_set = temp_filtered if len(temp_filtered) >= 2 else items

    # 2. 类别拆解
    parts = partition_by_category(working_set)
    tops = parts.get("top", [])
    bottoms = parts.get("bottom", [])
    coats = parts.get("coat", [])
    shoes = parts.get("shoes", [])

    # 如果分类后没有上衣或下装，尝试用全部非配饰单品自由组合
    if not tops and not bottoms:
        return [[item] for item in working_set[:5]]

    if not tops:
        tops = working_set[:3]
    if not bottoms:
        bottoms = working_set[:3]

    candidates: list[list[Any]] = []

    # 3. 组合生成 (Top x Bottom)
    for top in tops:
        for bottom in bottoms:
            if _get_val(top, "id") == _get_val(bottom, "id"):
                continue

            base_combo = [top, bottom]

            # 气温低于 22℃ 时尝试加入外套组合
            if current_temp <= 22.0 and coats:
                for coat in coats[:3]:
                    combo_with_coat = base_combo + [coat]
                    if shoes:
                        for shoe in shoes[:2]:
                            candidates.append(combo_with_coat + [shoe])
                    else:
                        candidates.append(combo_with_coat)

            # 纯上装+下装组合
            if shoes:
                for shoe in shoes[:2]:
                    candidates.append(base_combo + [shoe])
            else:
                candidates.append(base_combo)

            # 限制候选池最大规模，避免笛卡尔积过大
            if len(candidates) >= 120:
                break
        if len(candidates) >= 120:
            break

    return candidates if candidates else [working_set[:3]]


def item_to_detail(item: Any) -> OutfitItemDetail:
    """将 ORM 或字典实例转换为统一详情 Schema。"""
    item_id = str(_get_val(item, "id", uuid.uuid4().hex))
    return OutfitItemDetail(
        id=item_id,
        category=str(_get_val(item, "category", "top")),
        sub_category=str(_get_val(item, "sub_category", "clothing")),
        primary_color=str(_get_val(item, "primary_color", "black")),
        secondary_color=_get_val(item, "secondary_color"),
        style=str(_get_val(item, "style", "casual")),
        thickness=str(_get_val(item, "thickness", "medium")),
        image_url=str(_get_val(item, "image_url", "")),
        temp_min=float(_get_val(item, "temp_min", 15.0)),
        temp_max=float(_get_val(item, "temp_max", 25.0)),
    )


def recommend_outfits(
    items: list[Any],
    request: RecommendationRequest,
    user_preference: Any = None
) -> list[OutfitRecommendation]:
    """
    穿搭推荐核心决策主流程：
    1. 组合生成
    2. 多因素加权评分（气温、风格、场景、色彩与个性化偏好）
    3. 排序重排
    4. TOP-K 截断与人性化理由生成
    """
    candidates = generate_candidate_outfits(items, request.temperature)
    if not candidates:
        return []

    avoided_colors = set(_get_val(user_preference, "avoided_colors", []) or [])
    preferred_styles = set(_get_val(user_preference, "preferred_styles", []) or [])
    custom_weights = _get_val(user_preference, "custom_weights", None) or {}

    scored_outfits: list[OutfitRecommendation] = []

    for idx, combo in enumerate(candidates):
        w_score = score_outfit_weather(combo, request.temperature)
        s_score = score_outfit_style(combo, request.target_style)
        sc_score = score_outfit_scene(combo, request.scene)
        c_score = score_outfit_color(combo)
        
        # 基于用户偏好的个性化修正
        p_score = 0.8
        if avoided_colors:
            for it in combo:
                c1 = str(_get_val(it, "primary_color", ""))
                c2 = str(_get_val(it, "secondary_color", ""))
                if c1 in avoided_colors or c2 in avoided_colors:
                    p_score -= 0.3
        if preferred_styles:
            for it in combo:
                st = str(_get_val(it, "style", ""))
                if st in preferred_styles:
                    p_score += 0.1
        p_score = min(1.0, max(0.0, p_score))

        overall = calculate_overall_score(
            w_score, s_score, sc_score, c_score, p_score, custom_weights=custom_weights
        )

        breakdown = ScoreBreakdown(
            weather_score=round(w_score * 100, 1),
            style_score=round(s_score * 100, 1),
            scene_score=round(sc_score * 100, 1),
            color_score=round(c_score * 100, 1),
            overall_score=round(overall * 100, 1)
        )

        reason = generate_recommendation_reason(
            combo,
            request.temperature,
            request.scene,
            request.target_style,
            w_score,
            s_score,
            sc_score,
            c_score
        )

        scored_outfits.append(
            OutfitRecommendation(
                outfit_id=f"rec-{uuid.uuid4().hex[:8]}",
                items=[item_to_detail(it) for it in combo],
                scores=breakdown,
                reason=reason
            )
        )

    # 按综合得分降序重排
    scored_outfits.sort(key=lambda x: x.scores.overall_score, reverse=True)

    # 取 TOP-K 最优推荐方案
    return scored_outfits[:request.top_k]
