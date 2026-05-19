"""
app/routers/users.py

API endpoints for users.

Implements:
  - GET  /users                (with filters)
  - POST /users                (create)
  - PUT  /users/{user_id}       (update)

Supported query parameters for GET:
  - limit       max results, 1-100, default 20
  - latitude    latitude for geographic filtering
  - longitude   longitude for geographic filtering
  - radius_km   max distance in km; uses the Haversine formula to
                find users near the given lat/lng

Author: [Person 4 fills in]
Week 4
"""

import math

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserResponse, UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


# -------------------------------------------------------------------
# GET /users
# -------------------------------------------------------------------

@router.get("", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    latitude: float | None = Query(None),
    longitude: float | None = Query(None),
    radius_km: float | None = Query(None),
):
    """
    Return a list of users, optionally filtered by geographic radius.

    Implementation notes:
    - Start with db.query(User)
    - Exclude soft-deleted rows: filter User.deleted_at.is_(None)
    - If latitude, longitude AND radius_km are all provided:
        compute the Haversine distance from (latitude, longitude) to
        each user's stored location, and keep only those within radius_km
    - If only some of the three are provided, decide on sensible behavior
      (e.g. ignore the geo filter, or raise a 400). Document your choice.
    - Apply limit
    """
    query = db.query(User).filter(User.deleted_at.is_(None))

    if latitude is not None and longitude is not None and radius_km is not None:
        all_users = query.all()
        nearby = [
            u for u in all_users
            if haversine_km(latitude, longitude, u.latitude, u.longitude) <= radius_km
        ]
        return nearby[:limit]

    return query.limit(limit).all()


# -------------------------------------------------------------------
# POST /users
# -------------------------------------------------------------------

@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new user.
    - Build a User object from the payload
    - Consider handling duplicate emails gracefully (the email column
      is unique) — catch the error and return a 409 Conflict
    - add, commit, refresh, return
    """
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    new_user = User(**payload.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  
    return new_user


# -------------------------------------------------------------------
# PUT /users/{user_id}
# -------------------------------------------------------------------

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing user.
    - Look up the user by id
    - If not found, raise HTTPException(status_code=404, detail="...")
    - Apply only provided fields
    - commit, refresh, return
    """
    
    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


# -------------------------------------------------------------------
# HELPER
# -------------------------------------------------------------------

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth
    (in kilometers) using the Haversine formula.

    Steps:
    - convert degrees to radians
    - apply the Haversine formula
    - Earth radius ≈ 6371 km
    """
    R = 6371    

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))

    return R * c



