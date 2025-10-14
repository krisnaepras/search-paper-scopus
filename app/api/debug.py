"""
Debug endpoint untuk test API key flow
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, ApiKey
from app.core.dependencies import get_current_user
from app.core.security import decrypt_api_key
import requests

router = APIRouter(prefix="/api/debug", tags=["debug"])

@router.get("/test-flow")
async def test_api_key_flow(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Debug endpoint to test full API key flow"""
    
    result = {
        "user_email": current_user.email,
        "user_id": current_user.id
    }
    
    # Get API key from database
    api_key = db.query(ApiKey).filter(
        ApiKey.user_id == current_user.id,
        ApiKey.is_active == True
    ).first()
    
    if not api_key:
        return {**result, "error": "No active API key found"}
    
    result["api_key_id"] = api_key.id
    result["api_key_name"] = api_key.key_name
    result["encrypted_preview"] = api_key.api_key[:30] + "..."
    
    # Decrypt
    try:
        decrypted = decrypt_api_key(api_key.api_key)
        result["decrypted_key"] = decrypted
        result["decrypted_length"] = len(decrypted)
    except Exception as e:
        return {**result, "decrypt_error": str(e)}
    
    # Test with Scopus directly
    try:
        response = requests.get(
            "https://api.elsevier.com/content/search/scopus",
            headers={
                'X-ELS-APIKey': decrypted,
                'Accept': 'application/json'
            },
            params={'query': 'test', 'count': 1},
            timeout=10
        )
        
        result["scopus_status"] = response.status_code
        
        if response.status_code == 200:
            data = response.json()
            result["scopus_valid"] = True
            result["scopus_total_results"] = data.get('search-results', {}).get('opensearch:totalResults', 0)
        else:
            result["scopus_valid"] = False
            result["scopus_error"] = response.text[:200]
            
    except Exception as e:
        result["scopus_test_error"] = str(e)
    
    return result
