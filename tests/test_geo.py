import pytest
from app.services.geo import haversine_km, filter_nearby, validate_coordinates

class FakeActivity:
    def __init__(self, name, lat, lon):
        self.name = name
        self.latitude = lat
        self.longitude = lon

def test_haversine_same_point():
    assert haversine_km(42.0, 21.43, 42.0, 21.43) == 0.0

def test_haversine_known_distance():
    # Skopje to roughly 1 km north
    dist = haversine_km(42.0, 21.43, 42.009, 21.43)
    assert 0.9 < dist < 1.1

def test_filter_nearby_radius_1km():
    activities = [
        FakeActivity("here",    42.0,    21.43),
        FakeActivity("100m",    42.001,  21.43),
        FakeActivity("500m",    42.0045, 21.43),
        FakeActivity("2km",     42.018,  21.43),
        FakeActivity("far",     40.7128, -74.006),
    ]
    results = filter_nearby(42.0, 21.43, activities, radius_km=1.0)
    assert len(results) == 3

def test_filter_nearby_sorted():
    activities = [
        FakeActivity("far",   42.018, 21.43),
        FakeActivity("close", 42.001, 21.43),
    ]
    results = filter_nearby(42.0, 21.43, activities, radius_km=5.0)
    assert results[0][0].name == "close"

def test_filter_nearby_empty():
    assert filter_nearby(42.0, 21.43, [], radius_km=1.0) == []

def test_validate_coordinates_valid():
    validate_coordinates(42.0, 21.43)  # should not raise

def test_validate_coordinates_edges():
    validate_coordinates(-90, -180)
    validate_coordinates(90, 180)

def test_validate_coordinates_bad_lat():
    with pytest.raises(ValueError):
        validate_coordinates(91, 21.43)

def test_validate_coordinates_bad_lon():
    with pytest.raises(ValueError):
        validate_coordinates(42.0, 200)