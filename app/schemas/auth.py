"""
Authentication schemas for request/response
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """User registration schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Password")


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token payload data"""
    email: Optional[str] = None


class ApiKeyCreate(BaseModel):
    """Create API key schema"""
    key_name: str = Field(..., max_length=100, description="Name for this API key")
    api_key: str = Field(..., min_length=20, description="Scopus API key")


class ApiKeyResponse(BaseModel):
    """API key response schema"""
    id: int
    key_name: str
    is_active: bool
    created_at: datetime
    # Note: Never return the actual API key
    
    class Config:
        from_attributes = True


class WishlistCreate(BaseModel):
    """Create wishlist item schema"""
    title: str = Field(..., max_length=500)
    authors: Optional[str] = Field(None, max_length=500)
    year: Optional[str] = Field(None, max_length=10)
    publication: Optional[str] = Field(None, max_length=300)
    cited_by: Optional[int] = Field(0)
    doi: Optional[str] = Field(None, max_length=100)
    eid: Optional[str] = Field(None, max_length=100)
    scopus_url: Optional[str] = None
    notes: Optional[str] = None


class WishlistResponse(BaseModel):
    """Wishlist item response schema"""
    id: int
    title: str
    authors: Optional[str]
    year: Optional[str]
    publication: Optional[str]
    cited_by: int
    doi: Optional[str]
    eid: Optional[str]
    scopus_url: Optional[str]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
