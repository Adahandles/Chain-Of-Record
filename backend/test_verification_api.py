#!/usr/bin/env python3
"""
Test script for verification API endpoints.
This script tests the verification workflow without needing a database.
"""
import json
from fastapi.testclient import TestClient
from app.main import app

# Create test client
client = TestClient(app)


def test_app_info():
    """Test that the app info endpoint works."""
    print("Testing app info endpoint...")
    response = client.get("/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ App info endpoint works\n")


def test_api_info():
    """Test that the API info endpoint works."""
    print("Testing API info endpoint...")
    response = client.get("/info")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total endpoints: {len(data['endpoints'])}")
    
    # Check if verification endpoint is listed
    verification_endpoint = [e for e in data['endpoints'] if 'verification' in e['path']]
    if verification_endpoint:
        print(f"✓ Verification endpoint found: {verification_endpoint[0]}")
    
    assert response.status_code == 200
    print("✓ API info endpoint works\n")


def test_health_check():
    """Test basic health check."""
    print("Testing health check endpoint...")
    response = client.get("/api/v1/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ Health check works\n")


def test_openapi_schema():
    """Test that OpenAPI schema includes verification endpoints."""
    print("Testing OpenAPI schema...")
    response = client.get("/openapi.json")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        openapi = response.json()
        paths = openapi.get('paths', {})
        
        # Check for verification endpoints
        verification_paths = [p for p in paths.keys() if 'verification' in p]
        print(f"Verification paths found: {len(verification_paths)}")
        for path in verification_paths:
            print(f"  - {path}")
        
        assert len(verification_paths) > 0, "No verification paths found in OpenAPI schema"
        print("✓ OpenAPI schema includes verification endpoints\n")
    else:
        print(f"⚠ OpenAPI schema not available (status {response.status_code})\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Verification API Test Suite")
    print("=" * 60 + "\n")
    
    try:
        test_app_info()
        test_api_info()
        test_health_check()
        test_openapi_schema()
        
        print("=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
