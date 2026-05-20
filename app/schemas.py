from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr

# -------------------------------------------------------------------
# ACTIVITY SCHEMAS
# -------------------------------------------------------------------

class ActivityResponse(BaseModel):
    id: int
    name: str
    type: str
    subtype: Optional[str] = None
    phone_number: Optional[str] = None
    rating: Optional[float] = None
    user_rating_count: int
    latitude: float
    longitude: float
    working_hours: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    # deleted_at intentionally omitted - internal field

    # This lets Pydantic read directly from SQLAlchemy objects.
    model_config = ConfigDict(from_attributes=True)


class ActivityCreate(BaseModel):
    name: str
    type: Optional[str] = "other"
    subtype: Optional[str] = None
    phone_number: Optional[str] = None
    rating: Optional[float] = None
    user_rating_count: Optional[int] = 0
    latitude: float
    longitude: float
    working_hours: Optional[dict] = None

class ActivityUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    subtype: Optional[str] = None
    phone_number: Optional[str] = None
    rating: Optional[float] = None
    user_rating_count: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    working_hours: Optional[dict] = None


# -------------------------------------------------------------------
# USER SCHEMAS
# -------------------------------------------------------------------

class UserResponse(BaseModel):
    id: int
    name: str
    surname: str
    email: EmailStr
    destination: str
    latitude: float
    longitude: float
    created_at: datetime
    updated_at: datetime
    # deleted_at intentionally omitted — internal field


class UserCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr
    destination: str
    latitude: float
    longitude: float


class UserUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[EmailStr] = None
    destination: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


# -------------------------------------------------------------------
# RECOMMENDATION SCHEMAS
# -------------------------------------------------------------------

class ScoreBreakdown(BaseModel):
    distance: float
    rating: float
    popularity: float
    category_relevance: float
    final: float


class RecommendationItem(BaseModel):
    id: int
    name: str
    type: str
    subtype: str | None
    rating: float | None
    user_rating_count: int
    latitude: float
    longitude: float
    distance_km: float
    is_open: bool
    scores: ScoreBreakdown

    model_config = ConfigDict(from_attributes=True)


class RecommendationResponse(BaseModel):
    response_timestamp: str   # ISO 8601 with timezone
    context: str               # "breakfast" | "lunch" | "dinner" | "nightlife" | "general"
    radius_km: float
    user_latitude: float
    user_longitude: float
    count: int
    results: list[RecommendationItem]