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
    RELEVANCE_THRESHOLD,
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
        offset: int = 0,
) -> RecommendationResponse:
    response_timestamp = datetime.now(timezone.utc).astimezone()

    try:
        validated = validate_context(context)
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

        if resolved_context != "general" and scores["category_relevance"] < RELEVANCE_THRESHOLD:
            continue
        scored.append((activity, distance, scores))

    scored.sort(key=lambda item: item[2]["final"], reverse=True)
    top = scored[offset: offset + limit]

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
            working_hours=activity.working_hours,
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
        total=len(scored),   
        results=results,
    )


@router.get("/{user_id}", response_model=RecommendationResponse)
def recommendations_for_user(
        user_id: int,
        db: Session = Depends(get_db),
        radius_km: float = Query(DEFAULT_RADIUS_KM, gt=0, le=20),
        context: str | None = Query(None),
        limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
        offset: int = Query(0, ge=0),
):
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
        offset=offset,
    )


@router.get("", response_model=RecommendationResponse)
def recommendations_by_coordinates(
        db: Session = Depends(get_db),
        lat: float = Query(..., ge=-90, le=90),
        lon: float = Query(..., ge=-180, le=180),
        radius_km: float = Query(DEFAULT_RADIUS_KM, gt=0, le=20),
        context: str | None = Query(None),
        limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
        offset: int = Query(0, ge=0),
):
    validate_coordinates(lat, lon)

    return build_recommendations(
        db=db,
        user_lat=lat,
        user_lon=lon,
        radius_km=radius_km,
        context=context,
        limit=limit,
        offset=offset,
    )