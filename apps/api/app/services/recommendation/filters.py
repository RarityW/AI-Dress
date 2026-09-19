def filter_by_temperature(items: list[dict], current_temp: float) -> list[dict]:
    """
    Temperature filter: items outside [temp_min-3, temp_max+3] are excluded.
    """
    filtered = []
    for item in items:
        if (item["temp_min"] - 3) <= current_temp <= (item["temp_max"] + 3):
            filtered.append(item)
    return filtered
