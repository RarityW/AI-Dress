def score_weather(current_temp: float, optimal_temp: float) -> float:
    """Weather score uses linear decay from optimal temperature."""
    diff = abs(current_temp - optimal_temp)
    # Simple linear decay, 0 if diff > 10
    score = max(0.0, 1.0 - (diff / 10.0))
    return score

def score_style(item_style: str, target_style: str) -> float:
    """Style/Scene scores use simple match/partial-match logic."""
    if item_style.lower() == target_style.lower():
        return 1.0
    return 0.0

def score_scene(item_scene: str, target_scene: str) -> float:
    """Style/Scene scores use simple match/partial-match logic."""
    if item_scene.lower() == target_scene.lower():
        return 1.0
    return 0.0

def score_color(color1: str, color2: str) -> float:
    """Color score uses a basic compatibility matrix (neutrals=high, clash=low)."""
    neutrals = ["black", "white", "gray", "beige"]
    c1, c2 = color1.lower(), color2.lower()
    if c1 == c2:
        return 1.0
    if c1 in neutrals or c2 in neutrals:
        return 0.8
    # Simplified assumption
    return 0.5
