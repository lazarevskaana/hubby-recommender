"""
app/routers/recommendations.py

API endpoints for ranked, context-aware recommendations.

Endpoints:
  - GET /recommendations/{user_id}        uses the user's stored coordinates
  - GET /recommendations?lat=...&lon=...  uses coordinates from query params

Query parameters (both endpoints):
  - radius_km   (default 1.0)
  - context     ('breakfast' | 'lunch' | 'dinner' | 'nightlife' | 'general')
                 if omitted, inferred from the current time
  - limit       (default 10, max 50)

Author: Ana (Person 1)
Week 5
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Activity
from app.schemas import (
    RecommendationResponse,
    RecommendationItem,
    ScoreBreakdown,
)
from app.recommendations_config import (
    DEFAULT_RADIUS_KM,
    DEFAULT_LIMIT,
    MAX_LIMIT,
    RELEVANCE_THRESHOLD,   # add this
)
from app.services.geo import filter_nearby, validate_coordinates
from app.services.opening_hours import is_open_at
from app.services.context import infer_context, validate_context
from app.services.scoring import combined_score

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def build_recommendations(
    db: Session,
    user_lat: float,
    user_lon: float,
    radius_km: float,
    context: str | None,
    limit: int,
) -> RecommendationResponse:
    """
    The full recommendation pipeline:
    1. Capture response timestamp
    2. Resolve context (use given or infer from time)
    3. Load activities (exclude soft-deleted)
    4. Filter by distance
    5. Filter by 'is open at response_timestamp'
    6. Score each remaining activity
    7. Sort by final score descending, take top `limit`
    8. Build the response
    """
    response_timestamp = datetime.now(timezone.utc).astimezone()

    try:
        validated = validate_context(context)       # Predtoa vrakjase server error 500 a e 400 Bad Request.
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    resolved_context = validated if validated else infer_context(response_timestamp)


    activities = (
        db.query(Activity)
        .filter(Activity.deleted_at.is_(None))
        .all()
    )

    nearby = filter_nearby(user_lat, user_lon, activities, radius_km)

    open_nearby = [
        (activity, distance)
        for activity, distance in nearby
        if is_open_at(activity.working_hours, response_timestamp)
    ]

    # Hide activities that clearly don't match the requested context.
    # Cafes during dinner (0.3) are kept; bridges, museums, hotels (0.0) are dropped.
    # RELEVANCE_THRESHOLD = 0.3
    # Ova mora da e trgnato zatoa sto sega e isto ama nema sekogas da e isto

    scored = []
    for activity, distance in open_nearby:
        scores = combined_score(
            distance_km=distance,
            radius_km=radius_km,
            rating=activity.rating,
            user_rating_count=activity.user_rating_count,
            subtype=activity.subtype,
            context=resolved_context,
        )
        # Skip irrelevant activities — they don't fit the context.
        # Exception: 'general' context where everything is fair game.
        if resolved_context != "general" and scores["category_relevance"] < RELEVANCE_THRESHOLD:
            continue
        scored.append((activity, distance, scores))

    scored.sort(key=lambda item: item[2]["final"], reverse=True)
    top = scored[:limit]

    results = [
        RecommendationItem(
            id=activity.id,
            name=activity.name,
            type=activity.type,
            subtype=activity.subtype,
            rating=activity.rating,
            user_rating_count=activity.user_rating_count,
            latitude=activity.latitude,
            longitude=activity.longitude,
            distance_km=round(distance, 3),
            is_open=True,
            scores=ScoreBreakdown(
                distance=round(scores["distance"], 3),
                rating=round(scores["rating"], 3),
                popularity=round(scores["popularity"], 3),
                category_relevance=round(scores["category_relevance"], 3),
                final=round(scores["final"], 3),
            ),
        )
        for activity, distance, scores in top
    ]

    return RecommendationResponse(
        response_timestamp=response_timestamp.isoformat(),
        context=resolved_context,
        radius_km=radius_km,
        user_latitude=user_lat,
        user_longitude=user_lon,
        count=len(results),
        results=results,
    )


@router.get("/{user_id}", response_model=RecommendationResponse)
def recommendations_for_user(
    user_id: int,
    db: Session = Depends(get_db),
    radius_km: float = Query(DEFAULT_RADIUS_KM, gt=0, le=20),
    context: str | None = Query(None),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):
    """
    Recommendations for a user already in the database.
    Uses the user's stored latitude/longitude.
    Returns 404 if the user_id doesn't exist (or is soft-deleted).
    """
    user = (
        db.query(User)
        .filter(User.id == user_id, User.deleted_at.is_(None))
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return build_recommendations(
        db=db,
        user_lat=user.latitude,
        user_lon=user.longitude,
        radius_km=radius_km,
        context=context,
        limit=limit,
    )


@router.get("", response_model=RecommendationResponse)
def recommendations_by_coordinates(
    db: Session = Depends(get_db),
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(DEFAULT_RADIUS_KM, gt=0, le=20),
    context: str | None = Query(None),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):
    """
    Recommendations for an arbitrary point on the map.
    """
    validate_coordinates(lat, lon)

    return build_recommendations(
        db=db,
        user_lat=lat,
        user_lon=lon,
        radius_km=radius_km,
        context=context,
        limit=limit,
    )