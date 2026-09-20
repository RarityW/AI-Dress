"""
气象数据服务。
支持对接 Open-Meteo 实时气象数据、心知天气 (Seniverse) API，
并内置经纬度坐标解析、内存缓存与离线智能保底估算机制。
"""
import time
import logging
from typing import Any, Optional
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# 中国主流城市经纬度映射表 (纬度, 经度)
CITY_COORDINATES: dict[str, tuple[float, float]] = {
    "北京": (39.9042, 116.4074),
    "上海": (31.2304, 121.4737),
    "广州": (23.1291, 113.2644),
    "深圳": (22.5431, 114.0579),
    "杭州": (30.2741, 120.1551),
    "成都": (30.5728, 104.0668),
    "武汉": (30.5928, 114.3055),
    "南京": (32.0603, 118.7969),
    "西安": (34.3416, 108.9398),
    "重庆": (29.5630, 106.5516),
    "天津": (39.0842, 117.2008),
    "苏州": (31.2990, 120.5853),
    "长沙": (28.2282, 112.9388),
    "青岛": (36.0671, 120.3826),
    "厦门": (24.4798, 118.0894),
    "合肥": (31.8612, 117.2849),
    "福州": (26.0745, 119.2965),
    "昆明": (24.8801, 102.8329),
    "大连": (38.9140, 121.6147),
    "哈尔滨": (45.8038, 126.5349),
    "济南": (36.6512, 117.1201),
    "沈阳": (41.8057, 123.4315),
    "长春": (43.8868, 125.3245),
    "南昌": (28.6820, 115.8579),
    "郑州": (34.7466, 113.6253),
    "贵阳": (26.6470, 106.6302),
    "南宁": (22.8170, 108.3665),
    "海口": (20.0440, 110.1999),
    "三亚": (18.2528, 109.5119),
    "乌鲁木齐": (43.8256, 87.6168),
    "兰州": (36.0611, 103.8343),
    "银川": (38.4872, 106.2309),
    "西宁": (36.6171, 101.7782),
    "呼和浩特": (40.8415, 111.7510),
    "拉萨": (29.6500, 91.1000),
    "香港": (22.3193, 114.1694),
    "澳门": (22.1987, 113.5439),
    "台北": (25.0330, 121.5654),
}

# WMO 国际气象编码转换表
WMO_WEATHER_MAP: dict[int, tuple[str, str]] = {
    0: ("晴", "sunny"),
    1: ("晴朗少云", "sunny"),
    2: ("多云", "cloudy"),
    3: ("阴天", "overcast"),
    45: ("有雾", "foggy"),
    48: ("冻雾", "foggy"),
    51: ("小毛毛雨", "rainy"),
    53: ("毛毛雨", "rainy"),
    55: ("密毛毛雨", "rainy"),
    61: ("微量小雨", "rainy"),
    63: ("中雨", "rainy"),
    65: ("大雨", "rainy"),
    71: ("小雪", "snowy"),
    73: ("中雪", "snowy"),
    75: ("大雪", "snowy"),
    77: ("雪粒", "snowy"),
    80: ("小阵雨", "rainy"),
    81: ("阵雨", "rainy"),
    82: ("强阵雨", "rainy"),
    85: ("小阵雪", "snowy"),
    86: ("强阵雪", "snowy"),
    95: ("雷雨", "rainy"),
    96: ("雷雨伴有冰雹", "rainy"),
    99: ("强雷暴", "rainy"),
}

# 简单内存缓存：城市名 -> (时间戳, 气象数据)
_WEATHER_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
CACHE_TTL_SECONDS = 600.0  # 10 分钟缓存


def _get_fallback_weather(city: str) -> dict[str, Any]:
    """当所有网络 API 均不可用时的智能季节保底估算。"""
    # 针对部分南方城市和北方城市做区分
    is_south = any(s in city for s in ["广州", "深圳", "三亚", "海口", "厦门", "香港"])
    is_north = any(s in city for s in ["哈尔滨", "长春", "沈阳", "呼和浩特", "乌鲁木齐"])

    if is_south:
        temp = 26.0
    elif is_north:
        temp = 16.0
    else:
        temp = 21.0

    return {
        "city": city,
        "temperature": temp,
        "condition": "晴朗少云",
        "condition_code": "sunny",
        "humidity": 55.0,
        "wind_speed": 10.0,
        "feels_like": temp,
        "source": "fallback"
    }


async def get_realtime_weather(city: str) -> dict[str, Any]:
    """
    异步获取指定城市的实时气象数据。
    具备 10 分钟缓存、实时 Open-Meteo API 抓取与离线兜底。
    """
    clean_city = city.strip().replace("市", "").replace("特别行政区", "")

    # 1. 检查本地缓存
    now = time.time()
    if clean_city in _WEATHER_CACHE:
        cached_time, cached_data = _WEATHER_CACHE[clean_city]
        if now - cached_time < CACHE_TTL_SECONDS:
            return cached_data

    # 2. 如果配置了心知天气 Key，优先请求心知天气
    if settings.WEATHER_API_KEY:
        try:
            url = f"{settings.WEATHER_API_BASE_URL.rstrip('/')}/weather/now.json"
            params = {
                "key": settings.WEATHER_API_KEY,
                "location": clean_city,
                "language": "zh-Hans",
                "unit": "c"
            }
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    now_data = resp.json()["results"][0]["now"]
                    temp = float(now_data["temperature"])
                    cond_text = now_data["text"]
                    res = {
                        "city": city,
                        "temperature": temp,
                        "condition": cond_text,
                        "condition_code": "rainy" if "雨" in cond_text else "cloudy" if "云" in cond_text else "sunny",
                        "humidity": 60.0,
                        "wind_speed": 12.0,
                        "feels_like": temp,
                        "source": "seniverse"
                    }
                    _WEATHER_CACHE[clean_city] = (now, res)
                    return res
        except Exception as e:
            logger.warning(f"心知天气接口请求异常: {e}，尝试使用 Open-Meteo")

    # 3. 使用全免费、免注册的全球实时气象 API (Open-Meteo)
    coords = CITY_COORDINATES.get(clean_city)
    if not coords:
        # 如果未在精选表中，默认使用北京坐标，或者城市名模糊匹配
        matched = next((k for k in CITY_COORDINATES if k in clean_city or clean_city in k), None)
        coords = CITY_COORDINATES.get(matched, (39.9042, 116.4074))

    lat, lon = coords
    api_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,apparent_temperature"
    }

    try:
        async with httpx.AsyncClient(timeout=4.5) as client:
            resp = await client.get(api_url, params=params)
            if resp.status_code == 200:
                current = resp.json().get("current", {})
                temp = float(current.get("temperature_2m", 20.0))
                humidity = float(current.get("relative_humidity_2m", 50.0))
                wind = float(current.get("wind_speed_10m", 10.0))
                feels_like = float(current.get("apparent_temperature", temp))
                wmo_code = int(current.get("weather_code", 0))

                cond_name, cond_code = WMO_WEATHER_MAP.get(wmo_code, ("晴朗少云", "sunny"))

                res = {
                    "city": city,
                    "temperature": round(temp, 1),
                    "condition": cond_name,
                    "condition_code": cond_code,
                    "humidity": humidity,
                    "wind_speed": wind,
                    "feels_like": round(feels_like, 1),
                    "source": "open-meteo"
                }
                _WEATHER_CACHE[clean_city] = (now, res)
                return res
    except Exception as e:
        logger.warning(f"Open-Meteo 实时气象请求异常: {e}，进入保底模式")

    # 4. 保底方案
    fallback = _get_fallback_weather(city)
    return fallback


def get_weather(city: str) -> dict[str, Any]:
    """同步兼容入口。"""
    clean_city = city.strip().replace("市", "").replace("特别行政区", "")
    if clean_city in _WEATHER_CACHE:
        return _WEATHER_CACHE[clean_city][1]
    return _get_fallback_weather(city)
