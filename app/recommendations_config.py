"""
Team decisions for Week 5:
- Travel-app-focused weights (distance + context matter most)
- Sub-scores returned alongside the final score for explainability
"""

# -------------------------------------------------------------------
# SCORING WEIGHTS
# -------------------------------------------------------------------
SCORE_WEIGHTS = {
    "distance":           0.40,
    "category_relevance": 0.30,
    "rating":             0.20,
    "popularity":         0.10,
}

# Sanity check at import time — fail fast if someone edits this wrong.
assert abs(sum(SCORE_WEIGHTS.values()) - 1.0) < 1e-9, (
    "SCORE_WEIGHTS must sum to 1.0"
)


# -------------------------------------------------------------------
# RADIUS DEFAULTS
# -------------------------------------------------------------------
DEFAULT_RADIUS_KM = 1.0
DEFAULT_LIMIT = 10
MAX_LIMIT = 50


# -------------------------------------------------------------------
# CONTEXT TIME WINDOWS
# -------------------------------------------------------------------
# (start_hour_inclusive, end_hour_exclusive) in local 24h time.
# Tweak these if testing reveals weird edges.
CONTEXT_TIME_WINDOWS = {
    "breakfast": (6, 11),
    "lunch":     (11, 15),
    "general":   (15, 18),
    "dinner":    (18, 22),
    "nightlife": (22, 6),   
}


# -------------------------------------------------------------------
# CATEGORY RELEVANCE MAPS
# -------------------------------------------------------------------
# Map context -> {activity subtype: relevance score 0.0–1.0}.
# Anything not in the map for a given context defaults to 0.0.
# Subtypes here match the raw Google primary_type values from Week 3.
CATEGORY_RELEVANCE = {
    "breakfast": {
        "cafe": 1.0, "coffee_shop": 1.0, "bakery": 1.0, "cake_shop": 0.7,
        "restaurant": 0.4, "fast_food_restaurant": 0.4,
    },
    "lunch": {
        "restaurant": 1.0, "fast_food_restaurant": 0.9,
        "pizza_restaurant": 0.9, "italian_restaurant": 0.9,
        "meal_takeaway": 0.8, "cafe": 0.5, "bakery": 0.5,
    },
    "dinner": {
        "restaurant": 1.0, "italian_restaurant": 1.0,
        "pizza_restaurant": 0.9, "bar": 0.6,
        "fast_food_restaurant": 0.4, "cafe": 0.3,
    },
    "nightlife": {
        "bar": 1.0, "night_club": 1.0,
        "restaurant": 0.4, "cafe": 0.2,
    },
    "general": {
        # No strong context — everything gets a baseline 0.5.
        # Implementation note: a helper can return 0.5 for any unknown
        # subtype in the 'general' context.
    },
}

# Default relevance when a subtype isn't in the map for the given context.
DEFAULT_RELEVANCE_UNKNOWN = 0.0
DEFAULT_RELEVANCE_GENERAL = 0.5
RELEVANCE_THRESHOLD = 0.3