"""
app/schemas.py

Pydantic schemas — validation and serialization models that define the
shape of request and response JSON for the API.

These are SEPARATE from the SQLAlchemy models in models.py:
  - models.py  = database table structure
  - schemas.py = API input/output structure

Author: [Person 2 fills in]
Week 4
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


# -------------------------------------------------------------------
# ACTIVITY SCHEMAS
# -------------------------------------------------------------------

class ActivityResponse(BaseModel):
    """Shape of an activity returned in API responses."""
    # TODO: add fields matching the Activity model:
    #   id, name, type, subtype, phone_number, rating,
    #   user_rating_count, latitude, longitude, working_hours
    # Decide whether to expose created_at / updated_at / deleted_at.

    # This lets Pydantic read directly from SQLAlchemy objects.
    model_config = ConfigDict(from_attributes=True)


class ActivityCreate(BaseModel):
    """Shape of the JSON body when creating an activity (POST)."""
    # TODO: add the fields a client must/can provide to create an activity.
    pass


class ActivityUpdate(BaseModel):
    """Shape of the JSON body when updating an activity (PUT)."""
    # TODO: add fields. Make them Optional so partial updates are allowed.
    pass


# -------------------------------------------------------------------
# USER SCHEMAS
# -------------------------------------------------------------------

class UserResponse(BaseModel):
    """Shape of a user returned in API responses."""
    # TODO: add fields matching the User model:
    #   id, name, surname, email, destination, latitude, longitude
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """Shape of the JSON body when creating a user (POST)."""
    # TODO: add fields. Use EmailStr for the email so invalid emails
    #       are automatically rejected.
    pass


class UserUpdate(BaseModel):
    """Shape of the JSON body when updating a user (PUT)."""
    # TODO: add fields. Make them Optional for partial updates.
    pass