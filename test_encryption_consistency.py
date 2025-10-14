"""
Test encryption consistency
"""
from app.core.security import encrypt_api_key, decrypt_api_key, get_fernet_key

# Test API key
test_key = "73439d14c6dc73b3a06756cbc9de5a4a"

print("Testing encryption/decryption consistency:")
print(f"Original: {test_key}")

# Encrypt
encrypted1 = encrypt_api_key(test_key)
print(f"Encrypted 1: {encrypted1[:30]}...")

# Decrypt
decrypted1 = decrypt_api_key(encrypted1)
print(f"Decrypted 1: {decrypted1}")
print(f"Match: {test_key == decrypted1}")

# Test Fernet key
fernet_key = get_fernet_key()
print(f"\nFernet key (first 20 bytes): {fernet_key[:20]}")

# Now test with a key that's already in database
import os
from dotenv import load_dotenv
load_dotenv()

# Simulate what happens in FastAPI
from cryptography.fernet import Fernet
import hashlib
import base64
from app.core.config import settings

key_bytes = hashlib.sha256(settings.encryption_key.encode()).digest()
fernet_key2 = base64.urlsafe_b64encode(key_bytes)
cipher = Fernet(fernet_key2)

# Get encrypted key from database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

from app.db.models import ApiKey
key = db.query(ApiKey).filter(ApiKey.id == 8).first()  # User 3's key

if key:
    print(f"\n=== Database Key (ID 8) ===")
    print(f"Encrypted: {key.api_key[:30]}...")
    
    # Decrypt using app's decrypt function
    decrypted_app = decrypt_api_key(key.api_key)
    print(f"Decrypted (via app function): {decrypted_app}")
    
    # Decrypt using manual Fernet
    decrypted_manual = cipher.decrypt(key.api_key.encode()).decode()
    print(f"Decrypted (manual Fernet): {decrypted_manual}")
    
    # Test with Scopus
    import requests
    resp = requests.get(
        "https://api.elsevier.com/content/search/scopus",
        headers={'X-ELS-APIKey': decrypted_app, 'Accept': 'application/json'},
        params={'query': 'test', 'count': 1},
        timeout=10
    )
    print(f"\nScopus API test: {resp.status_code}")
    if resp.status_code != 200:
        print(f"Error: {resp.text[:200]}")

db.close()
