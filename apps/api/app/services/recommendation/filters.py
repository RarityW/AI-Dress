"""候选衣物过滤与分类规则。"""
from typing import Any


def _get_val(item: Any, key: str, default: Any = None) -> Any:
    """兼容易构对象（字典或 ORM 模型实例）获取属性。"""
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def filter_by_temperature(items: list[Any], current_temp: float, tolerance: float = 3.0) -> list[Any]:
    """
    气温硬约束过滤：
    单品适宜温度区间为 [temp_min, temp_max]。
    允许上下各 tolerance (默认 3℃) 的浮动。超出此范围的候选单品直接剔除。
    """
    filtered = []
    for item in items:
        t_min = _get_val(item, "temp_min")
        t_max = _get_val(item, "temp_max")
        if t_min is not None and t_max is not None:
            if (t_min - tolerance) <= current_temp <= (t_max + tolerance):
                filtered.append(item)
        else:
            # 未设定温度限制的单品（如四季配饰）默认保留
            filtered.append(item)
    return filtered


def partition_by_category(items: list[Any]) -> dict[str, list[Any]]:
    """按衣物主类别对候选衣物归类。"""
    partitions: dict[str, list[Any]] = {
        "top": [],
        "bottom": [],
        "coat": [],
        "shoes": [],
        "accessory": []
    }
    for item in items:
        cat = str(_get_val(item, "category", "")).lower()
        if cat in partitions:
            partitions[cat].append(item)
        else:
            # 兼容非标准归入上衣或下装
            partitions.setdefault(cat, []).append(item)
    return partitions
