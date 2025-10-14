"""
API Key management routes
Users can add, list, and delete their Scopus API keys
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db, User, ApiKey
from app.schemas.auth import ApiKeyCreate, ApiKeyResponse
from app.core.dependencies import get_current_user
from app.core.security import encrypt_api_key, decrypt_api_key

router = APIRouter(prefix="/api/keys", tags=["api-keys"])


@router.post("/", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a new Scopus API key for the current user
    """
    # Encrypt the API key before storing
    encrypted_key = encrypt_api_key(key_data.api_key)
    
    new_key = ApiKey(
        user_id=current_user.id,
        key_name=key_data.key_name,
        api_key=encrypted_key
    )
    
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    
    return new_key


@router.get("/", response_model=List[ApiKeyResponse])
async def get_user_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all API keys for the current user
    """
    keys = db.query(ApiKey).filter(ApiKey.user_id == current_user.id).all()
    return keys


@router.get("/active")
async def get_active_api_key(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the first active API key (decrypted) for making Scopus API calls
    Returns None if no active key found
    """
    key = db.query(ApiKey).filter(
        ApiKey.user_id == current_user.id,
        ApiKey.is_active == True
    ).first()
    
    if not key:
        return {"api_key": None, "message": "No active API key found. Please add one."}
    
    decrypted_key = decrypt_api_key(key.api_key)
    return {
        "api_key": decrypted_key,
        "key_name": key.key_name,
        "key_id": key.id
    }


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an API key
    """
    key = db.query(ApiKey).filter(
        ApiKey.id == key_id,
        ApiKey.user_id == current_user.id
    ).first()
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    db.delete(key)
    db.commit()
    
    return None


@router.patch("/{key_id}/toggle", response_model=ApiKeyResponse)
async def toggle_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Toggle API key active status
    """
    key = db.query(ApiKey).filter(
        ApiKey.id == key_id,
        ApiKey.user_id == current_user.id
    ).first()
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    key.is_active = not key.is_active
    db.commit()
    db.refresh(key)
    
    return key
