"""
Database models for User, ApiKey, and Wishlist
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    wishlists = relationship("Wishlist", back_populates="user", cascade="all, delete-orphan")


class ApiKey(Base):
    """API Key model - users can store their Scopus API keys"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key_name = Column(String(100), nullable=False)  # e.g., "My Scopus Key"
    api_key = Column(String(255), nullable=False)  # Encrypted Scopus API key
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="api_keys")


class Wishlist(Base):
    """Wishlist model - users can save papers"""
    __tablename__ = "wishlists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Paper information
    title = Column(String(500), nullable=False)
    authors = Column(String(500))
    year = Column(String(10))
    publication = Column(String(300))
    cited_by = Column(Integer, default=0)
    doi = Column(String(100))
    eid = Column(String(100), index=True)  # Scopus EID
    scopus_url = Column(Text)
    
    # Additional fields
    notes = Column(Text)  # User's personal notes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="wishlists")
