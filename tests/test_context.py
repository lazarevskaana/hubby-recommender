from datetime import datetime
import pytest
from app.services.context import infer_context, validate_context

def test_breakfast():
    assert infer_context(datetime(2026, 5, 21, 8, 0)) == "breakfast"

def test_lunch():
    assert infer_context(datetime(2026, 5, 21, 12, 0)) == "lunch"

def test_general():
    assert infer_context(datetime(2026, 5, 21, 16, 0)) == "general"

def test_dinner():
    assert infer_context(datetime(2026, 5, 21, 19, 0)) == "dinner"

def test_nightlife_before_midnight():
    assert infer_context(datetime(2026, 5, 21, 23, 0)) == "nightlife"

def test_nightlife_after_midnight():
    assert infer_context(datetime(2026, 5, 21, 2, 0)) == "nightlife"

def test_validate_context_valid():
    assert validate_context("lunch") == "lunch"
    assert validate_context("DINNER") == "dinner"

def test_validate_context_none():
    assert validate_context(None) is None

def test_validate_context_invalid():
    with pytest.raises(ValueError):
        validate_context("brunch")