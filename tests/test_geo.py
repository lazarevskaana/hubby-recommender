from app.services.geo import haversine_km, filter_nearby, validate_coordinates

# Mock activity object — geo.py doesn't need the full DB model,
# just something with latitude/longitude attributes.
class FakeActivity:
    def __init__(self, name, lat, lon):
        self.name = name
        self.latitude = lat
        self.longitude = lon

print("=" * 50)
print("Testing haversine_km:")
print("=" * 50)

# Same point — distance should be 0
d = haversine_km(42.0, 21.43, 42.0, 21.43)
print(f"  Same point:                  {d:.4f} km   expect: 0.0000")

# Very close (~111 meters at this latitude — 0.001 degree lat)
d = haversine_km(42.0, 21.43, 42.001, 21.43)
print(f"  ~111m apart:                 {d:.4f} km   expect: ~0.111")

# Known distance: Skopje city center to Skopje airport ~17 km
d = haversine_km(41.9981, 21.4254, 41.9617, 21.6214)
print(f"  Skopje center -> airport:    {d:.2f} km   expect: ~17 km")

# Across continents (should be thousands of km)
d = haversine_km(42.0, 21.43, 40.7128, -74.0060)  # Skopje to New York
print(f"  Skopje -> New York:          {d:.0f} km   expect: ~8000 km")

print()
print("=" * 50)
print("Testing filter_nearby:")
print("=" * 50)

# Activities at known distances from (42.0, 21.43)
activities = [
    FakeActivity("Right here",         42.0,    21.43),       # ~0 km
    FakeActivity("100m away",          42.001,  21.43),       # ~0.11 km
    FakeActivity("500m away",          42.0045, 21.43),       # ~0.5 km
    FakeActivity("2km away",           42.018,  21.43),       # ~2 km
    FakeActivity("Far away (NY)",      40.7128, -74.0060),    # ~8000 km
]

# Radius 1 km should keep first 3, drop the last 2
results = filter_nearby(42.0, 21.43, activities, radius_km=1.0)
print(f"  Radius 1 km — kept {len(results)} activities (expect 3):")
for activity, dist in results:
    print(f"    {activity.name}: {dist:.3f} km")

# Radius 5 km should keep first 4
results = filter_nearby(42.0, 21.43, activities, radius_km=5.0)
print(f"\n  Radius 5 km — kept {len(results)} activities (expect 4)")

# Empty list of activities should return empty
results = filter_nearby(42.0, 21.43, [], radius_km=1.0)
print(f"  Empty list:                  kept {len(results)} (expect 0)")

print()
print("=" * 50)
print("Testing validate_coordinates:")
print("=" * 50)

# Valid coordinates — should not raise
try:
    validate_coordinates(42.0, 21.43)
    print("  Valid (42.0, 21.43):         no error ✅")
except Exception as e:
    print(f"  Valid (42.0, 21.43):         RAISED ❌ ({e})")

try:
    validate_coordinates(-90, -180)
    print("  Edge (-90, -180):            no error ✅")
except Exception as e:
    print(f"  Edge (-90, -180):            RAISED ❌ ({e})")

try:
    validate_coordinates(90, 180)
    print("  Edge (90, 180):              no error ✅")
except Exception as e:
    print(f"  Edge (90, 180):              RAISED ❌ ({e})")

# Invalid latitude — should raise ValueError
try:
    validate_coordinates(91, 21.43)
    print("  Invalid lat=91:              NO ERROR ❌ (should raise)")
except ValueError:
    print("  Invalid lat=91:              ValueError raised ✅")

try:
    validate_coordinates(42, 200)
    print("  Invalid lon=200:             NO ERROR ❌ (should raise)")
except ValueError:
    print("  Invalid lon=200:             ValueError raised ✅")
