"""
app/routers/activities.py

API endpoints for activities.

Implements:
  - GET  /activities                  (with filters)
  - POST /activities                  (create)
  - PUT  /activities/{activity_id}     (update)

Supported query parameters for GET:
  - limit            max results, 1-100, default 20
  - category         filter by activity type/category
  - min_rating       filter by minimum rating
  - min_rating_count filter by minimum number of ratings
  - open_now         return only currently open activities

Author: [Person 3 fills in]
Week 4
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Activity
from app.schemas import ActivityResponse, ActivityCreate, ActivityUpdate

router = APIRouter(prefix="/activities", tags=["activities"])


# -------------------------------------------------------------------
# GET /activities
# -------------------------------------------------------------------

@router.get("", response_model=list[ActivityResponse])
def get_activities(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    category: str | None = Query(None),
    min_rating: float | None = Query(None),
    min_rating_count: int | None = Query(None),
    open_now: bool = Query(False),
):
    """
    Return a list of activities, filtered by the query parameters.

    Implementation notes:
    - Start with db.query(Activity)
    - Exclude soft-deleted rows: filter Activity.deleted_at.is_(None)
    - Apply each filter only if the parameter was provided
    - 'open_now': check the current weekday + time against the
      working_hours JSON. Helper function suggested below.
    - Apply .limit(limit) last
    """
    # TODO: implement
    pass


# -------------------------------------------------------------------
# POST /activities
# -------------------------------------------------------------------

@router.post("", response_model=ActivityResponse, status_code=201)
def create_activity(
    payload: ActivityCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new activity from the request body.
    - Build an Activity object from the payload
    - add, commit, refresh
    - return the created activity
    """
    # TODO: implement
    pass


# -------------------------------------------------------------------
# PUT /activities/{activity_id}
# -------------------------------------------------------------------

@router.put("/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: int,
    payload: ActivityUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing activity.
    - Look up the activity by id
    - If not found, raise HTTPException(status_code=404, detail="...")
    - Apply only the fields that were provided in the payload
    - commit, refresh, return
    """
    # TODO: implement
    pass


# -------------------------------------------------------------------
# HELPER
# -------------------------------------------------------------------

def is_open_now(working_hours: dict | None) -> bool:
    """
    Given a working_hours JSON dict, return True if the activity is
    currently open based on the server's current day and time.

    working_hours shape:
        {"monday": [{"open": "09:00", "close": "23:00"}], ..., "sunday": []}

    - None or missing day  -> treat as closed (return False)
    - empty list []        -> closed that day
    - check current time falls within any interval
    """
    # TODO: implement
    pass