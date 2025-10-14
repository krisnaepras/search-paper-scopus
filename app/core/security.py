"""
Security utilities - Password hashing, JWT tokens, encryption
"""

from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from cryptography.fernet import Fernet
import base64
import hashlib
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Encryption for API keys - generate proper Fernet key
def get_fernet_key() -> bytes:
    """Generate proper Fernet key from settings"""
    # Hash the key to get exactly 32 bytes
    key_bytes = hashlib.sha256(settings.encryption_key.encode()).digest()
    # Encode to url-safe base64
    return base64.urlsafe_b64encode(key_bytes)

try:
    cipher_suite = Fernet(get_fernet_key())
except Exception as e:
    print(f"Warning: Could not initialize Fernet cipher: {e}")
    # Generate a new key for this session
    cipher_suite = Fernet(Fernet.generate_key())


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    # Bcrypt has 72 byte limit, truncate if needed
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password - bcrypt has 72 byte limit"""
    # Bcrypt can only handle passwords up to 72 bytes
    # Truncate if longer (or pre-hash with SHA256 for very long passwords)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # For security, we'll use SHA256 first for long passwords
        password = hashlib.sha256(password_bytes).hexdigest()
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


def encrypt_api_key(api_key: str) -> str:
    """Encrypt API key before storing in database"""
    return cipher_suite.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt API key from database"""
    return cipher_suite.decrypt(encrypted_key.encode()).decode()
