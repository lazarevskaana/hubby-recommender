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

from datetime import datetime, time
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
    category: str | None = Query(None),          # maps to Activity.type
    min_rating: float | None = Query(None),
    min_rating_count: int | None = Query(None),  # maps to Activity.user_rating_count
    open_now: bool = Query(False),
):
    """
    Return a list of activities, filtered by the query parameters.
    """
    query = db.query(Activity).filter(Activity.deleted_at.is_(None))

    if category is not None:
        query = query.filter(Activity.type == category)

    if min_rating is not None:
        query = query.filter(Activity.rating >= min_rating)

    if min_rating_count is not None:
        query = query.filter(Activity.user_rating_count >= min_rating_count)

    activities = query.limit(limit).all()

    # open_now can't be pushed to SQL — working_hours is a JSON column,
    # so we evaluate it in Python after fetching.
    if open_now:
        activities = [a for a in activities if is_open_now(a.working_hours)]

    return activities


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
    """
    activity = Activity(**payload.model_dump())
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


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
    """
    activity = (
        db.query(Activity)
        .filter(Activity.id == activity_id, Activity.deleted_at.is_(None))
        .first()
    )

    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(activity, field, value)

    db.commit()
    db.refresh(activity)
    return activity


# -------------------------------------------------------------------
# HELPER
# -------------------------------------------------------------------

# Monday=0 … Sunday=6, matching Python's datetime.weekday()
_DAY_NAMES = [
    "monday", "tuesday", "wednesday", "thursday",
    "friday", "saturday", "sunday",
]


def is_open_now(working_hours: dict | None) -> bool:
    """
    Given a working_hours JSON dict, return True if the activity is
    currently open based on the server's current day and time.

    working_hours shape:
        {"monday": [{"open": "09:00", "close": "23:00"}], ..., "sunday": []}

    - None or missing day  -> treat as closed (return False)
    - empty list []        -> closed that day
    - checks current time against every interval for today
    - handles overnight slots where close < open  (e.g. 22:00 – 02:00)
    """
    if not working_hours:
        return False

    today = _DAY_NAMES[datetime.now().weekday()]
    slots = working_hours.get(today)

    if not slots:           # key missing or empty list -> closed
        return False

    now_t = datetime.now().time().replace(second=0, microsecond=0)

    for slot in slots:
        try:
            open_h,  open_m  = map(int, slot["open"].split(":"))
            close_h, close_m = map(int, slot["close"].split(":"))
        except (KeyError, ValueError):
            continue        # malformed slot — skip rather than crash

        open_t  = time(open_h,  open_m)
        close_t = time(close_h, close_m)

        if open_t <= close_t:
            # Normal slot  e.g. 09:00 – 23:00
            if open_t <= now_t < close_t:
                return True
        else:
            # Overnight slot  e.g. 22:00 – 02:00
            # Open if:  now >= 22:00  OR  now < 02:00
            if now_t >= open_t or now_t < close_t:
                return True

    return False