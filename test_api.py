"""
Simple test script for API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_register():
    """Test registration"""
    print("Testing registration...")
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"email": "testuser1@example.com", "password": "testpass123"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    return response.json()

def test_login():
    """Test login"""
    print("Testing login...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "testuser1@example.com", "password": "testpass123"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Token: {data.get('access_token', 'N/A')[:50]}...\n")
    return data

def test_add_api_key(token):
    """Test adding API key"""
    print("Testing add API key...")
    response = requests.post(
        f"{BASE_URL}/api/keys",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "key_name": "Test Scopus Key",
            "api_key": "bfa6c12f7a3f9c5f6ce3ed21bdeb5a5a",
            "is_active": True
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    return response.json()

def test_search(token):
    """Test search endpoint"""
    print("Testing search...")
    response = requests.post(
        f"{BASE_URL}/api/search",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "query": "machine learning",
            "limit": 5
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total found: {data.get('total_found', 0)}")
        print(f"Papers returned: {len(data.get('papers', []))}")
    else:
        print(f"Error: {response.json()}")
    return response

if __name__ == "__main__":
    print("=== API Testing ===\n")
    
    # Register (might fail if user exists, that's OK)
    try:
        test_register()
    except Exception as e:
        print(f"Registration failed (user might exist): {e}\n")
    
    # Login
    login_data = test_login()
    token = login_data.get("access_token")
    
    if not token:
        print("Failed to get token. Stopping tests.")
        exit(1)
    
    # Add API key
    test_add_api_key(token)
    
    # Test search
    test_search(token)
    
    print("\n=== Tests completed ===")
