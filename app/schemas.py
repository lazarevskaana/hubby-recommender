"""
app/schemas.py

Pydantic schemas — validation and serialization models that define the
shape of request and response JSON for the API.

These are SEPARATE from the SQLAlchemy models in models.py:
  - models.py  = database table structure
  - schemas.py = API input/output structure

Author: [David Gjorgjievski]
Week 4
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr

# -------------------------------------------------------------------
# ACTIVITY SCHEMAS
# -------------------------------------------------------------------

class ActivityResponse(BaseModel):
    """Shape of an activity returned in API responses."""
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
    """Shape of the JSON body when creating an activity (POST)."""
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
    """Shape of the JSON body when updating an activity (PUT)."""
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
    """Shape of a user returned in API responses."""
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
    """Shape of the JSON body when creating a user (POST)."""
    name: str
    surname: str
    email: EmailStr
    destination: str
    latitude: float
    longitude: float


class UserUpdate(BaseModel):
    """Shape of the JSON body when updating a user (PUT)."""
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[EmailStr] = None
    destination: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
