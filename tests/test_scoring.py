from app.services.scoring import (
    distance_score, rating_score, popularity_score,
    category_relevance, combined_score,
)

def test_distance_score_at_origin():
    assert distance_score(0.0, 1.0) == 1.0

def test_distance_score_at_edge():
    assert distance_score(1.0, 1.0) == 0.0

def test_distance_score_beyond_radius():
    assert distance_score(2.0, 1.0) == 0.0

def test_distance_score_zero_radius():
    assert distance_score(0.0, 0.0) == 0.0

def test_rating_score():
    assert rating_score(5.0) == 1.0
    assert rating_score(0.0) == 0.0
    assert rating_score(None) == 0.0

def test_popularity_score_zero():
    assert popularity_score(0) == 0.0

def test_popularity_score_capped():
    assert popularity_score(100000) == 1.0

def test_category_relevance_general():
    assert category_relevance("museum", "general") == 0.5
    assert category_relevance(None, "general") == 0.0

def test_category_relevance_match():
    assert category_relevance("restaurant", "lunch") == 1.0

def test_category_relevance_miss():
    assert category_relevance("museum", "lunch") == 0.0

def test_combined_score_keys():
    result = combined_score(0.1, 1.0, 4.5, 100, "restaurant", "lunch")
    assert set(result.keys()) == {"distance", "rating", "popularity", "category_relevance", "final"}

def test_combined_score_range():
    result = combined_score(0.1, 1.0, 4.5, 100, "restaurant", "lunch")
    assert 0.0 <= result["final"] <= 1.0