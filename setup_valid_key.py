"""
Add valid Scopus API key untuk testing
"""
import requests

BASE_URL = "http://localhost:8000"

# Ganti dengan API key Scopus yang valid
VALID_API_KEY = input("Masukkan Scopus API key yang valid: ").strip()

if not VALID_API_KEY or VALID_API_KEY == "":
    print("❌ API key tidak boleh kosong!")
    exit(1)

print("\n[1] Testing API key directly to Scopus...")
response = requests.get(
    "https://api.elsevier.com/content/search/scopus",
    headers={
        'X-ELS-APIKey': VALID_API_KEY,
        'Accept': 'application/json'
    },
    params={'query': 'test', 'count': 1},
    timeout=10
)

if response.status_code == 200:
    print("✅ API key VALID!")
    data = response.json()
    total = data.get('search-results', {}).get('opensearch:totalResults', 0)
    print(f"   Total results: {total}")
else:
    print(f"❌ API key INVALID! Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
    exit(1)

# Login
print("\n[2] Login to application...")
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"email": "testuser1@example.com", "password": "testpass123"}
)
token = response.json()["access_token"]
print("✅ Logged in")

# Delete old keys
print("\n[3] Deleting old API keys...")
response = requests.get(
    f"{BASE_URL}/api/keys",
    headers={"Authorization": f"Bearer {token}"}
)
old_keys = response.json()
for key in old_keys:
    requests.delete(
        f"{BASE_URL}/api/keys/{key['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
print(f"✅ Deleted {len(old_keys)} old keys")

# Add new valid key
print("\n[4] Adding valid API key...")
response = requests.post(
    f"{BASE_URL}/api/keys",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "key_name": "Valid Scopus Key",
        "api_key": VALID_API_KEY,
        "is_active": True
    }
)
print(f"✅ API key added: {response.json()}")

# Test search
print("\n[5] Testing search endpoint...")
response = requests.post(
    f"{BASE_URL}/api/search",
    headers={"Authorization": f"Bearer {token}"},
    json={"query": "machine learning", "limit": 5},
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    print("✅ SEARCH BERHASIL!")
    print(f"   Total available: {data['total_available']}")
    print(f"   Returned: {data['returned_count']}")
    print(f"   Execution time: {data['execution_time']:.2f}s")
    print(f"\n   First paper: {data['papers'][0]['title']}")
else:
    print(f"❌ Search failed: {response.json()}")

print("\n" + "="*60)
print("DONE! Aplikasi siap digunakan dengan API key valid.")
print("="*60)
