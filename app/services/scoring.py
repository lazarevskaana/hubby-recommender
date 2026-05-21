import math

from app.recommendations_config import (
    SCORE_WEIGHTS,
    CATEGORY_RELEVANCE,
    DEFAULT_RELEVANCE_UNKNOWN,
    DEFAULT_RELEVANCE_GENERAL,
)


def distance_score(distance_km: float, radius_km: float) -> float:
    """
    1.0 when the activity is at the user's exact location.
    0.0 when at the edge of the radius.
    Beyond the radius is clamped to 0.0 (caller should already have
    filtered, but be defensive).

    Formula: 1 - (distance_km / radius_km), clamped to [0, 1]
    """
    if radius_km <= 0:
        return 0.0

    return max(0.0, min(1.0, 1 - (distance_km / radius_km)))


def rating_score(rating: float | None) -> float:
    """
    Rating / 5. None or 0 -> 0.0.
    """
    if not rating:
        return 0.0
    return rating / 5.0


def popularity_score(user_rating_count: int | None) -> float:
    """
    log10(count + 1) / 4, clamped to max 1.0.
    None or 0 -> 0.0.

    Examples (approximate):
        0    -> 0.00
        10   -> 0.26
        100  -> 0.50
        1000 -> 0.75
        10000+ -> 1.00
    """
    if not user_rating_count:
        return 0.0
    return min(1.0, math.log10(user_rating_count + 1) / 4)


def category_relevance(subtype: str | None, context: str) -> float:
    if subtype is None:
        return 0.0
    if context == "general":
        return DEFAULT_RELEVANCE_GENERAL
    return CATEGORY_RELEVANCE.get(context, {}).get(subtype, DEFAULT_RELEVANCE_UNKNOWN)



def combined_score(
    distance_km: float,
    radius_km: float,
    rating: float | None,
    user_rating_count: int | None,
    subtype: str | None,
    context: str,
) -> dict:
    d = distance_score(distance_km, radius_km)
    r = rating_score(rating)
    p = popularity_score(user_rating_count)
    c = category_relevance(subtype, context)

    final = (
        SCORE_WEIGHTS["distance"] * d
        + SCORE_WEIGHTS["rating"] * r
        + SCORE_WEIGHTS["popularity"] * p
        + SCORE_WEIGHTS["category_relevance"] * c
    )

    return {
        "distance": d,
        "rating": r,
        "popularity": p,
        "category_relevance": c,
        "final": final,
    }
