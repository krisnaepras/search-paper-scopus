"""
Direct database query to check encryption/decryption
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Get API key from database
from app.db.models import ApiKey
from app.core.security import decrypt_api_key

print("="*60)
print("DATABASE API KEY CHECK")
print("="*60)

# Get all API keys
keys = db.query(ApiKey).all()
print(f"\nTotal API keys in database: {len(keys)}")

for idx, key in enumerate(keys, 1):
    print(f"\n[{idx}] Key ID: {key.id}")
    print(f"    User ID: {key.user_id}")
    print(f"    Name: {key.key_name}")
    print(f"    Active: {key.is_active}")
    print(f"    Encrypted (preview): {key.api_key[:30]}...")
    
    # Try to decrypt
    try:
        decrypted = decrypt_api_key(key.api_key)
        print(f"    Decrypted: {decrypted}")
        
        # Test with Scopus
        import requests
        response = requests.get(
            "https://api.elsevier.com/content/search/scopus",
            headers={
                'X-ELS-APIKey': decrypted,
                'Accept': 'application/json'
            },
            params={'query': 'test', 'count': 1},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"    ✅ VALID - Scopus API works!")
        elif response.status_code == 401 or response.status_code == 403:
            print(f"    ❌ INVALID - Scopus returned {response.status_code}")
        else:
            print(f"    ⚠️  Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"    ❌ Decryption error: {e}")

db.close()

print("\n" + "="*60)
