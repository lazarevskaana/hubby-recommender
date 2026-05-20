"""
app/services/opening_hours.py

Check whether an activity is open at a specific timestamp, using the
working_hours JSON stored in the database.

working_hours shape:
    {
      "monday":    [{"open": "09:00", "close": "23:00"}],
      "tuesday":   [{"open": "09:00", "close": "23:00"}],
      ...
      "sunday":    []                                 # closed
    }
    or None -> treat as closed (conservative default)

Author: [Person 3 fills in]
Week 5
"""

from datetime import datetime, time


# Day index 0 = Monday, 6 = Sunday — matches Python's weekday()
DAY_NAMES = ["monday", "tuesday", "wednesday", "thursday",
             "friday", "saturday", "sunday"]


def is_open_at(working_hours: dict | None, when: datetime) -> bool:
    """
    Return True if the activity is open at `when`.

    Conservative rules:
      - working_hours is None -> closed (we don't know)
      - that weekday's value is missing or None -> closed
      - that weekday's value is [] -> closed
      - non-empty list -> check whether `when`'s time falls inside ANY
        of the intervals
    """
    # TODO: implement
    # Hints:
    #   day_name = DAY_NAMES[when.weekday()]
    #   intervals = working_hours.get(day_name) if working_hours else None
    #   parse "09:00" -> time(9, 0)
    #   return any(start <= when.time() <= end for start, end in intervals)
    pass


def _parse_hhmm(hhmm: str) -> time:
    """Parse a 'HH:MM' string into a datetime.time. Helper."""
    # TODO: implement
    pass