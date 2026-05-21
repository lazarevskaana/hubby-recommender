from datetime import datetime
from app.services.context import infer_context, validate_context

# infer_context — time-of-day mapping
print("Testing infer_context:")
print(f"  08:00 -> {infer_context(datetime(2026, 5, 21, 8, 0))}   expect: breakfast")
print(f"  10:59 -> {infer_context(datetime(2026, 5, 21, 10, 59))} expect: breakfast")
print(f"  11:00 -> {infer_context(datetime(2026, 5, 21, 11, 0))}  expect: lunch")
print(f"  13:00 -> {infer_context(datetime(2026, 5, 21, 13, 0))}  expect: lunch")
print(f"  14:59 -> {infer_context(datetime(2026, 5, 21, 14, 59))} expect: lunch")
print(f"  15:00 -> {infer_context(datetime(2026, 5, 21, 15, 0))}  expect: general")
print(f"  17:00 -> {infer_context(datetime(2026, 5, 21, 17, 0))}  expect: general")
print(f"  18:00 -> {infer_context(datetime(2026, 5, 21, 18, 0))}  expect: dinner")
print(f"  20:00 -> {infer_context(datetime(2026, 5, 21, 20, 0))}  expect: dinner")
print(f"  22:00 -> {infer_context(datetime(2026, 5, 21, 22, 0))}  expect: nightlife")
print(f"  23:00 -> {infer_context(datetime(2026, 5, 21, 23, 0))}  expect: nightlife")
print(f"  02:00 -> {infer_context(datetime(2026, 5, 21, 2, 0))}   expect: nightlife (wraps midnight)")
print(f"  05:00 -> {infer_context(datetime(2026, 5, 21, 5, 0))}   expect: nightlife")
print(f"  06:00 -> {infer_context(datetime(2026, 5, 21, 6, 0))}   expect: breakfast (boundary)")
print()

# validate_context
print("Testing validate_context:")
print(f"  None      -> {validate_context(None)}        expect: None")
print(f"  'lunch'   -> {validate_context('lunch')}     expect: lunch")
print(f"  'DINNER'  -> {validate_context('DINNER')}    expect: dinner (lowercased)")
print(f"  'Breakfast' -> {validate_context('Breakfast')} expect: breakfast")
print()

# Should raise ValueError
print("Testing validate_context with invalid input:")
try:
    validate_context("brunch")
    print("  'brunch' -> NO ERROR RAISED ❌ (should have raised ValueError)")
except ValueError as e:
    print(f"  'brunch' -> ValueError raised ✅ ({e})")
