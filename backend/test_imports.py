"""Test imports step by step to find what's blocking"""
import time

def test_import(name, import_func):
    start = time.time()
    try:
        import_func()
        elapsed = time.time() - start
        print(f"OK {name}: {elapsed:.3f}s")
        return True, elapsed
    except Exception as e:
        elapsed = time.time() - start
        print(f"FAIL {name}: {elapsed:.3f}s - ERROR: {e}")
        return False, elapsed

print("Testing imports step by step...\n")

# Test 1: Basic FastAPI
test_import("FastAPI", lambda: __import__('fastapi').FastAPI())

# Test 2: Database
test_import("Database", lambda: __import__('backend.data.database', fromlist=['']))

# Test 3: Services
test_import("MonitoringService", lambda: __import__('backend.services.monitoring_service', fromlist=['']))
test_import("ValidationService", lambda: __import__('backend.services.validation_service', fromlist=['']))

# Test 4: DescriptionService (should be fast now)
test_import("DescriptionService", lambda: __import__('backend.services.description_service', fromlist=['']))

# Test 5: Full api_controller
print("\nTesting full api_controller import (this might hang)...")
start = time.time()
try:
    from backend.api_controller import app
    elapsed = time.time() - start
    print(f"✓ api_controller: {elapsed:.3f}s")
    print(f"  Routes: {len(app.routes)}")
except Exception as e:
    elapsed = time.time() - start
    print(f"✗ api_controller: {elapsed:.3f}s - ERROR: {e}")
    import traceback
    traceback.print_exc()

