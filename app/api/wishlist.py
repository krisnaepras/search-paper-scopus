"""
Wishlist API routes
Users can save, list, and delete papers from their wishlist
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db, User, Wishlist
from app.schemas.auth import WishlistCreate, WishlistResponse
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/wishlist", tags=["wishlist"])


@router.post("/", response_model=WishlistResponse, status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    item_data: WishlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a paper to user's wishlist
    """
    # Check if already in wishlist (by EID if available)
    if item_data.eid:
        existing = db.query(Wishlist).filter(
            Wishlist.user_id == current_user.id,
            Wishlist.eid == item_data.eid
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Paper already in wishlist"
            )
    
    # Create new wishlist item
    new_item = Wishlist(
        user_id=current_user.id,
        **item_data.model_dump()
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return new_item


@router.get("/", response_model=List[WishlistResponse])
async def get_wishlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all papers in user's wishlist
    """
    items = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id
    ).order_by(Wishlist.created_at.desc()).all()
    
    return items


@router.get("/{item_id}", response_model=WishlistResponse)
async def get_wishlist_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific wishlist item
    """
    item = db.query(Wishlist).filter(
        Wishlist.id == item_id,
        Wishlist.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wishlist item not found"
        )
    
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_from_wishlist(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a paper from wishlist
    """
    item = db.query(Wishlist).filter(
        Wishlist.id == item_id,
        Wishlist.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wishlist item not found"
        )
    
    db.delete(item)
    db.commit()
    
    return None


@router.patch("/{item_id}/notes", response_model=WishlistResponse)
async def update_wishlist_notes(
    item_id: int,
    notes: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update notes for a wishlist item
    """
    item = db.query(Wishlist).filter(
        Wishlist.id == item_id,
        Wishlist.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wishlist item not found"
        )
    
    item.notes = notes
    db.commit()
    db.refresh(item)
    
    return item


@router.get("/check/{eid}")
async def check_in_wishlist(
    eid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check if a paper (by EID) is in wishlist
    """
    item = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id,
        Wishlist.eid == eid
    ).first()
    
    return {
        "in_wishlist": item is not None,
        "wishlist_id": item.id if item else None
    }
