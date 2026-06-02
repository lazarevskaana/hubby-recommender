
import math

from fastapi import APIRouter, Depends, Query, HTTPException

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserResponse, UserCreate, UserUpdate
from app.services.geo import haversine_km

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

    query = db.query(User).filter(User.deleted_at.is_(None))

    if latitude is not None and longitude is not None and radius_km is not None:
        all_users = query.all()
        nearby = [
            u for u in all_users
            if haversine_km(latitude, longitude, u.latitude, u.longitude) <= radius_km
        ]
        return nearby[:limit]

    return query.limit(limit).all()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a single user by ID."""
    user = (
        db.query(User)
        .filter(User.id == user_id, User.deleted_at.is_(None))
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# -------------------------------------------------------------------
# POST /users
# -------------------------------------------------------------------

@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
):
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

    
    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user



