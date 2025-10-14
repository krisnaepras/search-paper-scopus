"""
Debug script untuk melihat error detail dari search endpoint
"""
import requests
import json
import traceback

BASE_URL = "http://localhost:8000"

def debug_search():
    """Debug search with detailed error output"""
    
    # Step 1: Login
    print("=== Step 1: Login ===")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "testuser@example.com", "password": "testpass123"},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Login failed: {response.text}")
            return
        
        token = response.json()["access_token"]
        print(f"✓ Login successful\n")
    except Exception as e:
        print(f"✗ Login error: {e}\n")
        traceback.print_exc()
        return
    
    # Step 2: Check API keys
    print("=== Step 2: List API Keys ===")
    try:
        response = requests.get(
            f"{BASE_URL}/api/keys",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        keys = response.json()
        print(f"API Keys found: {len(keys)}")
        for key in keys:
            print(f"  - {key['key_name']}: Active={key['is_active']}")
        print()
    except Exception as e:
        print(f"✗ Get keys error: {e}\n")
        traceback.print_exc()
    
    # Step 3: Search
    print("=== Step 3: Search ===")
    try:
        print("Sending search request...")
        response = requests.post(
            f"{BASE_URL}/api/search",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "query": "machine learning",
                "limit": 5
            },
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Search successful!")
            print(f"  Total available: {data.get('total_available', 0)}")
            print(f"  Papers returned: {data.get('returned_count', 0)}")
            print(f"  Execution time: {data.get('execution_time', 0):.2f}s")
        else:
            print(f"✗ Search failed!")
            print(f"Response body:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
        
    except requests.exceptions.Timeout:
        print("✗ Request timeout!")
    except Exception as e:
        print(f"✗ Search error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_search()
