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
    # TODO: implement
    pass


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
    # TODO: implement
    pass


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
    # TODO: implement
    pass


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
    # TODO: implement
    pass