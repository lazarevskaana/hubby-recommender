"""
app/services/context.py

Context handling — inferring the meal/time context from a timestamp
when the caller didn't specify one.

Author: [Person 4 fills in]
Week 5
"""

from datetime import datetime
from app.recommendations_config import CONTEXT_TIME_WINDOWS


VALID_CONTEXTS = {"breakfast", "lunch", "dinner", "nightlife", "general"}


def infer_context(when: datetime) -> str:
    """
    Map a datetime to a meal context based on the hour of day.
    Reads CONTEXT_TIME_WINDOWS from recommendations_config.

    Returns one of: 'breakfast', 'lunch', 'dinner', 'nightlife', 'general'.

    Note: 'nightlife' wraps midnight (22:00 to 06:00). Handle that case.
    """
    # TODO: implement
    # hour = when.hour
    # for context, (start, end) in CONTEXT_TIME_WINDOWS.items():
    #     if context == "nightlife": handle wrap (start <= hour or hour < end)
    #     else: start <= hour < end
    pass


def validate_context(context: str | None) -> str:
    """
    Validate a user-provided context string.
    - If None, return None (caller will infer).
    - If a valid context name, return it lowercased.
    - Otherwise raise ValueError with the list of valid options.
    """
    # TODO: implement
    pass