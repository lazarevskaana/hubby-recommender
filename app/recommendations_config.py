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
MAX_LIMIT = 500


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
        "cafe": 1.0, "coffee_shop": 1.0, "bakery": 1.0, "pastry_shop": 1.0,
        "cake_shop": 0.8, "donut_shop": 0.9, "cafeteria": 0.8, "dessert_restaurant": 0.6,
        "bistro": 0.6, "restaurant": 0.4, "fast_food_restaurant": 0.4,
        "hamburger_restaurant": 0.3, "meal_takeaway": 0.4,
    },
    "lunch": {
        "restaurant": 1.0, "fast_food_restaurant": 0.9, "pizza_restaurant": 0.9,
        "italian_restaurant": 0.9, "hamburger_restaurant": 0.9, "meal_takeaway": 0.8,
        "vegetarian_restaurant": 0.9, "vegan_restaurant": 0.9, "mexican_restaurant": 0.9,
        "sushi_restaurant": 0.9, "barbecue_restaurant": 0.9, "seafood_restaurant": 0.9,
        "eastern_european_restaurant": 0.9, "soul_food_restaurant": 0.9, "bistro": 0.9,
        "gastropub": 0.7, "cafeteria": 0.7, "cafe": 0.5, "bakery": 0.5,
    },
    "dinner": {
        "restaurant": 1.0, "italian_restaurant": 1.0, "vegetarian_restaurant": 1.0,
        "vegan_restaurant": 1.0, "mexican_restaurant": 1.0, "sushi_restaurant": 1.0,
        "barbecue_restaurant": 1.0, "seafood_restaurant": 1.0, "soul_food_restaurant": 1.0,
        "eastern_european_restaurant": 1.0, "bistro": 1.0, "pizza_restaurant": 0.9,
        "hamburger_restaurant": 0.8, "gastropub": 0.8, "bar": 0.6, "wine_bar": 0.6,
        "fast_food_restaurant": 0.4, "meal_takeaway": 0.4, "cafe": 0.3,
    },
    "nightlife": {
        "bar": 1.0, "cocktail_bar": 1.0, "wine_bar": 1.0, "lounge_bar": 1.0,
        "irish_pub": 1.0, "gastropub": 0.8, "event_venue": 0.8, "movie_theater": 0.7,
        "restaurant": 0.4, "cafe": 0.2,
    },
    "general": {
        "museum": 1.0, "art_museum": 1.0, "history_museum": 1.0, "art_gallery": 1.0,
        "tourist_attraction": 1.0, "cultural_center": 0.9, "church": 0.8, "mosque": 0.8,
        "bridge": 0.7, "playground": 0.7, "movie_theater": 0.8, "event_venue": 0.7,
        "hotel": 0.5, "restaurant": 0.5, "cafe": 0.5, "coffee_shop": 0.5, "bar": 0.4,
        # any subtype not listed here falls to DEFAULT_RELEVANCE_UNKNOWN (0.0)
    },
}













# Default relevance when a subtype isn't in the map for the given context.
DEFAULT_RELEVANCE_UNKNOWN = 0.0
DEFAULT_RELEVANCE_GENERAL = 0.5
RELEVANCE_THRESHOLD = 0.3