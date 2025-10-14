"""
Check API key dari database dan test langsung ke Scopus
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"

def check_api_keys():
    """Check API keys in database"""
    
    # Login
    print("=== Login ===")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "testuser1@example.com", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    print("✓ Logged in\n")
    
    # Get API keys
    print("=== API Keys in Database ===")
    response = requests.get(
        f"{BASE_URL}/api/keys",
        headers={"Authorization": f"Bearer {token}"}
    )
    keys = response.json()
    
    for idx, key in enumerate(keys, 1):
        print(f"\n{idx}. {key['key_name']}")
        print(f"   ID: {key['id']}")
        print(f"   Active: {key['is_active']}")
        print(f"   API Key: {key['api_key'][:10]}...{key['api_key'][-10:]}")
        print(f"   Created: {key['created_at']}")
        
        # Test this API key directly to Scopus
        print(f"   Testing with Scopus API...", end=" ")
        test_response = requests.get(
            "https://api.elsevier.com/content/search/scopus",
            headers={
                'X-ELS-APIKey': key['api_key'],
                'Accept': 'application/json'
            },
            params={
                'query': 'machine learning',
                'count': 1
            },
            timeout=10
        )
        
        if test_response.status_code == 200:
            print("✓ VALID")
            data = test_response.json()
            total = data.get('search-results', {}).get('opensearch:totalResults', 0)
            print(f"   Total results available: {total}")
        elif test_response.status_code == 401:
            print("✗ INVALID (401 Unauthorized)")
        else:
            print(f"✗ ERROR ({test_response.status_code})")
            print(f"   Response: {test_response.text[:200]}")
    
    # Also check default API key from env
    print("\n\n=== Default API Key from .env ===")
    default_key = os.getenv("SCOPUS_API_KEY", "")
    if default_key:
        print(f"Key: {default_key[:10]}...{default_key[-10:]}")
        print("Testing with Scopus API...", end=" ")
        test_response = requests.get(
            "https://api.elsevier.com/content/search/scopus",
            headers={
                'X-ELS-APIKey': default_key,
                'Accept': 'application/json'
            },
            params={
                'query': 'machine learning',
                'count': 1
            },
            timeout=10
        )
        
        if test_response.status_code == 200:
            print("✓ VALID")
            data = test_response.json()
            total = data.get('search-results', {}).get('opensearch:totalResults', 0)
            print(f"Total results: {total}")
        elif test_response.status_code == 401:
            print("✗ INVALID (401 Unauthorized)")
        else:
            print(f"✗ ERROR ({test_response.status_code})")
    else:
        print("No default API key in .env")

if __name__ == "__main__":
    check_api_keys()
