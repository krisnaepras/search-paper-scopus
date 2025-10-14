"""
Debug encryption/decryption issue
"""
from app.core.security import encrypt_api_key, decrypt_api_key

# Test API key
test_key = "73439d14c6dc73b3a06756cbc9de5a4a"

print("="*60)
print("ENCRYPTION/DECRYPTION TEST")
print("="*60)

print(f"\nOriginal key: {test_key}")
print(f"Length: {len(test_key)}")

# Encrypt
encrypted = encrypt_api_key(test_key)
print(f"\nEncrypted: {encrypted}")
print(f"Length: {len(encrypted)}")

# Decrypt
decrypted = decrypt_api_key(encrypted)
print(f"\nDecrypted: {decrypted}")
print(f"Length: {len(decrypted)}")

# Verify
if test_key == decrypted:
    print("\n✅ Encryption/Decryption working correctly!")
else:
    print("\n❌ MISMATCH!")
    print(f"Expected: {test_key}")
    print(f"Got: {decrypted}")

# Now test with key from database
print("\n" + "="*60)
print("TEST WITH DATABASE KEY")
print("="*60)

import requests

# Login
response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"email": "testuser1@example.com", "password": "testpass123"}
)
token = response.json()["access_token"]

# Get active key (already decrypted by endpoint)
response = requests.get(
    "http://localhost:8000/api/keys/active",
    headers={"Authorization": f"Bearer {token}"}
)
data = response.json()
db_decrypted_key = data["api_key"]

print(f"\nKey from /api/keys/active: {db_decrypted_key}")
print(f"Length: {len(db_decrypted_key)}")

# Test this key directly
print("\nTesting key directly with Scopus...")
import requests as req
test_response = req.get(
    "https://api.elsevier.com/content/search/scopus",
    headers={
        'X-ELS-APIKey': db_decrypted_key,
        'Accept': 'application/json'
    },
    params={'query': 'test', 'count': 1},
    timeout=10
)

if test_response.status_code == 200:
    print(f"✅ Key from database works! Total results: {test_response.json()['search-results']['opensearch:totalResults']}")
else:
    print(f"❌ Key failed! Status: {test_response.status_code}")
    print(f"Response: {test_response.text[:200]}")
