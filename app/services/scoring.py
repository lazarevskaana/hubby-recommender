"""
app/services/scoring.py

The four sub-scores and the final combined recommendation score.
Each function returns a value between 0.0 and 1.0.

All scoring decisions are deterministic — same inputs always produce
the same outputs (no randomness).

Author: 
Week 5
"""

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
    # TODO: implement
    pass


def rating_score(rating: float | None) -> float:
    """
    Rating / 5. None or 0 -> 0.0.
    """
    # TODO: implement
    pass


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
    # TODO: implement
    pass


def category_relevance(subtype: str | None, context: str) -> float:
    """
    Look up the subtype in the CATEGORY_RELEVANCE map for this context.

    - If context == "general": return DEFAULT_RELEVANCE_GENERAL (0.5)
      for every subtype (no strong preference).
    - Else: look up subtype in CATEGORY_RELEVANCE[context]. Missing
      subtype -> DEFAULT_RELEVANCE_UNKNOWN (0.0).
    - subtype is None -> 0.0
    """
    # TODO: implement
    pass


def combined_score(
    distance_km: float,
    radius_km: float,
    rating: float | None,
    user_rating_count: int | None,
    subtype: str | None,
    context: str,
) -> dict:
    """
    Compute all four sub-scores and the weighted final score.
    Returns a dict matching the ScoreBreakdown schema:
        {
            "distance": ...,
            "rating": ...,
            "popularity": ...,
            "category_relevance": ...,
            "final": ...,
        }

    Final formula uses SCORE_WEIGHTS from recommendations_config.
    """
    # TODO: implement using the four functions above
    pass