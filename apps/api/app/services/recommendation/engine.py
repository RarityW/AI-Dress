from app.core.config import settings

def calculate_overall_score(
    weather_score: float,
    style_score: float,
    scene_score: float,
    color_score: float,
    preference_score: float
) -> float:
    """
    Combine scores: S = Σ(w_i × s_i)
    """
    total = (
        settings.WEIGHT_WEATHER * weather_score +
        settings.WEIGHT_STYLE * style_score +
        settings.WEIGHT_SCENE * scene_score +
        settings.WEIGHT_COLOR * color_score +
        settings.WEIGHT_PREFERENCE * preference_score
    )
    return min(1.0, max(0.0, total))
