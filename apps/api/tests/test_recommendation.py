from app.services.recommendation.engine import calculate_overall_score
from app.services.recommendation.filters import filter_by_temperature
from app.services.recommendation.scorer import score_weather, score_style, score_color

def test_calculate_overall_score():
    score = calculate_overall_score(1.0, 1.0, 1.0, 1.0, 1.0)
    assert score == 1.0
    
def test_filter_by_temperature():
    items = [
        {"id": 1, "temp_min": 15, "temp_max": 25},
        {"id": 2, "temp_min": 5, "temp_max": 10},
    ]
    filtered = filter_by_temperature(items, 20.0)
    assert len(filtered) == 1
    assert filtered[0]["id"] == 1
    
def test_score_weather():
    assert score_weather(20.0, 20.0) == 1.0
    assert score_weather(20.0, 30.0) == 0.0
    
def test_score_style():
    assert score_style("casual", "casual") == 1.0
    assert score_style("formal", "casual") == 0.0

def test_score_color():
    assert score_color("red", "red") == 1.0
    assert score_color("black", "red") == 0.8
    assert score_color("red", "blue") == 0.5
