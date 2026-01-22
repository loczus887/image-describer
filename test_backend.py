#!/usr/bin/env python3
"""Simple test script to check if backend is responding"""
import requests
import sys

def test_backend():
    base_url = "http://localhost:8000"
    
    print("Testing backend endpoints...")
    print(f"Base URL: {base_url}\n")
    
    # Test health
    print("1. Testing /health...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ERROR: Cannot connect to backend. Is it running?")
        return False
    except requests.exceptions.Timeout:
        print("   ERROR: Request timed out")
        return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    print()
    
    # Test model status
    print("2. Testing /model-status...")
    try:
        response = requests.get(f"{base_url}/model-status", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    print("\n[OK] All tests passed!")
    return True

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("ERROR: requests library not installed")
        print("Install it with: pip install requests")
        sys.exit(1)
    
    success = test_backend()
    sys.exit(0 if success else 1)

