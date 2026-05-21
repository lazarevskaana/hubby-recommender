from app.services.scoring import (
    distance_score, rating_score, popularity_score,
    category_relevance, combined_score
)

print("category_relevance('museum', 'general') =", category_relevance("museum", "general"))
print("category_relevance(None, 'lunch') =", category_relevance(None, "lunch"))
print()
print("combined_score test:")
result = combined_score(
    distance_km=0.1,
    radius_km=1.0,
    rating=4.5,
    user_rating_count=100,
    subtype="restaurant",
    context="lunch",
)
for k, v in result.items():
    print(f"  {k}: {round(v, 4)}")
