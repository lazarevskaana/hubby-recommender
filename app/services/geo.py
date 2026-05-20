"""
app/services/geo.py

Geographic helpers — Haversine distance and nearby-activity filtering.

Author:
Week 5
"""

import math
from typing import Sequence


EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Great-circle distance between two lat/lng points in kilometers.

    Steps:
    1. Convert all four coordinates from degrees to radians.
    2. Apply the Haversine formula.
    3. Multiply by Earth's radius (6371 km).
    """
    # TODO: implement
    # If you wrote this in Week 4 for the users router, move/reuse that code here.
    pass


def filter_nearby(
    user_lat: float,
    user_lon: float,
    activities: Sequence,
    radius_km: float,
) -> list[tuple]:
    """
    Given a user location and a list of Activity ORM objects, return
    only those within `radius_km`, paired with their distance.

    Returns: list of (activity, distance_km) tuples.
    """
    # TODO: implement
    # For each activity:
    #   dist = haversine_km(user_lat, user_lon, activity.latitude, activity.longitude)
    #   if dist <= radius_km: keep (activity, dist)
    pass


def validate_coordinates(lat: float, lon: float) -> None:
    """
    Validate that lat/lon are in valid ranges.
    Raises ValueError with a clear message if not.
        latitude:  -90 to 90
        longitude: -180 to 180
    """
    # TODO: implement
    pass