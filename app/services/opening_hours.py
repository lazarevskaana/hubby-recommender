from datetime import datetime, time

DAY_NAMES = ["monday", "tuesday", "wednesday", "thursday",
             "friday", "saturday", "sunday"]


def is_open_at(working_hours: dict | None, when: datetime) -> bool:
    day_name = DAY_NAMES[when.weekday()]
    intervals = working_hours.get(day_name) if working_hours else None

    if not intervals:
        return False

    current = when.time()
    for interval in intervals:
        start = _parse_hhmm(interval["open"])
        end = _parse_hhmm(interval["close"])
        if start <= end:
            if start <= current < end:
                return True
        else:
            # Overnight e.g. 22:00–02:00
            if current >= start or current < end:
                return True

    return False

def _parse_hhmm(hhmm: str) -> time:
    
    hour, minute = hhmm.split(":")
    return time(int(hour), int(minute))