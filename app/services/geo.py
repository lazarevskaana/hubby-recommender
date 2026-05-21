import math
from typing import Sequence
 
 
EARTH_RADIUS_KM = 6371.0
 
 
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
  
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
 
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(a))
 
 
def filter_nearby(
    user_lat: float,
    user_lon: float,
    activities: Sequence,
    radius_km: float,
) -> list[tuple]:
   
    validate_coordinates(user_lat, user_lon)
 
    results: list[tuple] = []
    for activity in activities:
        dist = haversine_km(user_lat, user_lon, activity.latitude, activity.longitude)
        if dist <= radius_km:
            results.append((activity, dist))
 
    results.sort(key=lambda pair: pair[1])
    return results
 
 
def validate_coordinates(lat: float, lon: float) -> None:
    
    if not (-90.0 <= lat <= 90.0):
        raise ValueError(f"Latitude {lat!r} is out of range -90..90")
    if not (-180.0 <= lon <= 180.0):
        raise ValueError(f"Longitude {lon!r} is out of range -180..180")
 