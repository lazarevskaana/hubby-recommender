from datetime import datetime
import pytest
from app.services.opening_hours import is_open_at

normal_hours = {
    "monday":    [{"open": "09:00", "close": "23:00"}],
    "tuesday":   [{"open": "09:00", "close": "23:00"}],
    "wednesday": [{"open": "09:00", "close": "23:00"}],
    "thursday":  [{"open": "09:00", "close": "23:00"}],
    "friday":    [{"open": "09:00", "close": "23:00"}],
    "saturday":  [{"open": "09:00", "close": "23:00"}],
    "sunday":    [],
}

split_hours = {
    "monday": [{"open": "09:00", "close": "13:00"}, {"open": "15:00", "close": "19:00"}],
    **{d: [] for d in ["tuesday","wednesday","thursday","friday","saturday","sunday"]},
}

overnight_hours = {
    "friday":   [{"open": "22:00", "close": "02:00"}],
    "saturday": [{"open": "22:00", "close": "02:00"}],
    **{d: [] for d in ["monday","tuesday","wednesday","thursday","sunday"]},
}

all_day = {d: [{"open": "00:00", "close": "23:59"}] for d in
           ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]}

def test_open_during_hours():
    assert is_open_at(normal_hours, datetime(2026, 5, 21, 13, 0)) is True

def test_before_opening():
    assert is_open_at(normal_hours, datetime(2026, 5, 21, 8, 0)) is False

def test_after_closing():
    assert is_open_at(normal_hours, datetime(2026, 5, 21, 23, 30)) is False

def test_exact_opening_time():
    assert is_open_at(normal_hours, datetime(2026, 5, 21, 9, 0)) is True

def test_closed_day():
    assert is_open_at(normal_hours, datetime(2026, 5, 24, 13, 0)) is False

def test_split_morning():
    assert is_open_at(split_hours, datetime(2026, 5, 25, 10, 0)) is True

def test_split_lunch_break():
    assert is_open_at(split_hours, datetime(2026, 5, 25, 14, 0)) is False

def test_split_afternoon():
    assert is_open_at(split_hours, datetime(2026, 5, 25, 16, 0)) is True

def test_overnight_before_midnight():
    # Friday 23:00 — should be open
    assert is_open_at(overnight_hours, datetime(2026, 5, 22, 23, 0)) is True

def test_overnight_after_midnight():
    # Saturday 01:00 — should be open (crosses midnight from Friday)
    assert is_open_at(overnight_hours, datetime(2026, 5, 23, 1, 0)) is True

def test_overnight_after_close():
    # Saturday 03:00 — should be closed
    assert is_open_at(overnight_hours, datetime(2026, 5, 23, 3, 0)) is False

def test_all_day():
    assert is_open_at(all_day, datetime(2026, 5, 21, 3, 0)) is True

def test_none_hours():
    assert is_open_at(None, datetime(2026, 5, 21, 13, 0)) is False

def test_empty_dict():
    assert is_open_at({}, datetime(2026, 5, 21, 13, 0)) is False

def test_missing_day():
    assert is_open_at({"monday": [{"open": "09:00", "close": "23:00"}]},
                      datetime(2026, 5, 21, 13, 0)) is False