from datetime import datetime
from app.services.opening_hours import is_open_at

print("=" * 50)
print("Testing is_open_at:")
print("=" * 50)

# Typical week — open 9 AM to 11 PM every day except Sunday
normal_hours = {
    "monday":    [{"open": "09:00", "close": "23:00"}],
    "tuesday":   [{"open": "09:00", "close": "23:00"}],
    "wednesday": [{"open": "09:00", "close": "23:00"}],
    "thursday":  [{"open": "09:00", "close": "23:00"}],
    "friday":    [{"open": "09:00", "close": "23:00"}],
    "saturday":  [{"open": "09:00", "close": "23:00"}],
    "sunday":    [],   # closed Sunday
}

# 2026-05-21 is a Thursday
print("\nNormal hours (open 09:00-23:00, closed Sundays):")
print(f"  Thu 13:00 (lunchtime):       {is_open_at(normal_hours, datetime(2026, 5, 21, 13, 0))}   expect: True")
print(f"  Thu 08:00 (before opening):  {is_open_at(normal_hours, datetime(2026, 5, 21, 8, 0))}   expect: False")
print(f"  Thu 23:30 (after closing):   {is_open_at(normal_hours, datetime(2026, 5, 21, 23, 30))}  expect: False")
print(f"  Thu 09:00 (exact opening):   {is_open_at(normal_hours, datetime(2026, 5, 21, 9, 0))}   expect: True")
print(f"  Sun 13:00 (closed day):      {is_open_at(normal_hours, datetime(2026, 5, 24, 13, 0))}  expect: False")

# Activity with split intervals (lunch break)
split_hours = {
    "monday":    [{"open": "09:00", "close": "13:00"}, {"open": "15:00", "close": "19:00"}],
    "tuesday":   [],
    "wednesday": [],
    "thursday":  [],
    "friday":    [],
    "saturday":  [],
    "sunday":    [],
}

print("\nSplit hours (Mon 09:00-13:00 + 15:00-19:00):")
print(f"  Mon 10:00 (morning shift):   {is_open_at(split_hours, datetime(2026, 5, 25, 10, 0))}  expect: True")
print(f"  Mon 14:00 (lunch break):     {is_open_at(split_hours, datetime(2026, 5, 25, 14, 0))}  expect: False")
print(f"  Mon 16:00 (afternoon):       {is_open_at(split_hours, datetime(2026, 5, 25, 16, 0))}  expect: True")
print(f"  Mon 20:00 (after close):     {is_open_at(split_hours, datetime(2026, 5, 25, 20, 0))}  expect: False")

# 24-hour activity
all_day = {
    "monday":    [{"open": "00:00", "close": "23:59"}],
    "tuesday":   [{"open": "00:00", "close": "23:59"}],
    "wednesday": [{"open": "00:00", "close": "23:59"}],
    "thursday":  [{"open": "00:00", "close": "23:59"}],
    "friday":    [{"open": "00:00", "close": "23:59"}],
    "saturday":  [{"open": "00:00", "close": "23:59"}],
    "sunday":    [{"open": "00:00", "close": "23:59"}],
}

print("\n24-hour activity:")
print(f"  Thu 03:00 (middle of night): {is_open_at(all_day, datetime(2026, 5, 21, 3, 0))}   expect: True")
print(f"  Thu 12:00 (noon):            {is_open_at(all_day, datetime(2026, 5, 21, 12, 0))}  expect: True")

# Edge cases — defensive handling
print("\nEdge cases:")
print(f"  working_hours=None:          {is_open_at(None, datetime(2026, 5, 21, 13, 0))}  expect: False")
print(f"  Empty dict {{}}:              {is_open_at({}, datetime(2026, 5, 21, 13, 0))}  expect: False")

missing_day = {"monday": [{"open": "09:00", "close": "23:00"}]}  # only Monday defined
print(f"  Missing day (Thu not in):    {is_open_at(missing_day, datetime(2026, 5, 21, 13, 0))}  expect: False")

day_is_none = {"thursday": None}
print(f"  Day value is None:           {is_open_at(day_is_none, datetime(2026, 5, 21, 13, 0))}  expect: False")
