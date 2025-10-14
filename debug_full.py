"""
Comprehensive debugging untuk mencari masalah API key
"""
import requests
import sys

BASE_URL = "http://localhost:8000"

def test_full_flow():
    print("="*60)
    print("COMPREHENSIVE API KEY DEBUGGING")
    print("="*60)
    
    # Step 1: Login
    print("\n[1] LOGIN")
    print("-" * 40)
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "testuser1@example.com", "password": "testpass123"},
            timeout=5
        )
        if response.status_code != 200:
            print(f"❌ Login failed: {response.json()}")
            return
        
        token = response.json()["access_token"]
        print(f"✅ Login successful")
        print(f"   Token: {token[:30]}...")
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 2: Get active API key via endpoint
    print("\n[2] GET ACTIVE API KEY (via /api/keys/active)")
    print("-" * 40)
    try:
        response = requests.get(
            f"{BASE_URL}/api/keys/active",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        active_key_data = response.json()
        print(f"Response: {active_key_data}")
        
        if active_key_data.get("api_key"):
            decrypted_key = active_key_data["api_key"]
            print(f"✅ Active API key found")
            print(f"   Key name: {active_key_data.get('key_name')}")
            print(f"   Key preview: {decrypted_key[:10]}...{decrypted_key[-10:]}")
        else:
            print("❌ No active API key found")
            return
    except Exception as e:
        print(f"❌ Error getting active key: {e}")
        return
    
    # Step 3: Test API key directly with Scopus
    print("\n[3] TEST API KEY DIRECTLY WITH SCOPUS")
    print("-" * 40)
    try:
        print(f"Testing key: {decrypted_key[:10]}...{decrypted_key[-10:]}")
        response = requests.get(
            "https://api.elsevier.com/content/search/scopus",
            headers={
                'X-ELS-APIKey': decrypted_key,
                'Accept': 'application/json'
            },
            params={
                'query': 'machine learning',
                'count': 1,
                'view': 'STANDARD'
            },
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            total = data.get('search-results', {}).get('opensearch:totalResults', 0)
            print(f"✅ API key is VALID!")
            print(f"   Total results available: {total}")
        elif response.status_code == 401:
            print(f"❌ API key is INVALID (401 Unauthorized)")
            print(f"   Response: {response.text[:300]}")
        elif response.status_code == 429:
            print(f"⚠️  Rate limit exceeded (429)")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
    except Exception as e:
        print(f"❌ Direct test error: {e}")
    
    # Step 4: Test via search endpoint
    print("\n[4] TEST VIA SEARCH ENDPOINT (/api/search)")
    print("-" * 40)
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
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search successful!")
            print(f"   Total available: {data.get('total_available', 0)}")
            print(f"   Papers returned: {data.get('returned_count', 0)}")
            print(f"   Execution time: {data.get('execution_time', 0):.2f}s")
        else:
            print(f"❌ Search failed!")
            error_data = response.json()
            print(f"   Error: {error_data.get('message', error_data)}")
    except Exception as e:
        print(f"❌ Search endpoint error: {e}")
    
    # Step 5: Check what's in database
    print("\n[5] CHECK DATABASE - ALL API KEYS")
    print("-" * 40)
    try:
        response = requests.get(
            f"{BASE_URL}/api/keys",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        keys = response.json()
        print(f"Total keys in database: {len(keys)}")
        
        for idx, key in enumerate(keys, 1):
            print(f"\n   Key {idx}:")
            print(f"   - ID: {key['id']}")
            print(f"   - Name: {key['key_name']}")
            print(f"   - Active: {key['is_active']}")
            print(f"   - Created: {key['created_at']}")
    except Exception as e:
        print(f"❌ Error listing keys: {e}")
    
    print("\n" + "="*60)
    print("DEBUGGING COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_full_flow()
