from datetime import datetime
from app.recommendations_config import CONTEXT_TIME_WINDOWS


VALID_CONTEXTS = {"breakfast", "lunch", "dinner", "nightlife", "general"}


def infer_context(when: datetime) -> str:
    hour = when.hour
    for context, (start, end) in CONTEXT_TIME_WINDOWS.items():
        if context == "nightlife":
            if hour >= start or hour < end:
                return context
        else:
            if start <= hour < end:
                return context
            
    return "general"
    



def validate_context(context: str | None) -> str:
    if context is None:
        return None
    
    lowered = context.lower()

    if lowered in VALID_CONTEXTS:
        return lowered
    
    raise ValueError(
        f"Invalid context '{context}'. Valid options are: {sorted(VALID_CONTEXTS)}"
    )