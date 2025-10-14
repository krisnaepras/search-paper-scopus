# 🎯 Migration Guide - Old to New Architecture

## Quick Start

### 1. Install New Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Environment

```bash
cp .env.example .env
# Edit .env and add your SCOPUS_API_KEY
```

### 3. Run New Server

```bash
python run.py
```

---

## Architecture Comparison

### Old Structure (api_scopus.py)

```
api_scopus.py (677 lines)
├── All imports
├── Configuration (hard-coded)
├── Enums
├── Models
├── Helper functions
├── API endpoints
├── Error handlers
└── Server runner
```

### New Structure (Clean Architecture)

```
app/
├── main.py              # App initialization (95 lines)
├── api/                 # Controllers (6 files, ~300 lines)
├── core/                # Configuration (2 files, ~70 lines)
├── schemas/             # Data models (5 files, ~180 lines)
└── services/            # Business logic (1 file, ~200 lines)
```

**Result**: Better organized, easier to maintain, more scalable!

---

## Key Changes

### 1. Configuration

**Before:**

```python
API_KEY = "73439d14c6dc73b3a06756cbc9de5a4a"  # Hard-coded
SCOPUS_BASE_URL = "https://..."
```

**After:**

```python
# In .env file
SCOPUS_API_KEY=your_key_here

# In app/core/config.py
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    scopus_api_key: str
    ...
```

### 2. Routes

**Before:**

```python
@app.post("/api/search")
async def search_papers(request: SearchRequest):
    # 50+ lines of logic here
    ...
```

**After:**

```python
# In app/api/search.py
@router.post("/search")
async def search_papers(request: SearchRequest):
    # Delegate to service
    papers, query, total = scopus_service.search_papers(...)
    return SearchResponse(...)
```

### 3. Business Logic

**Before:** Mixed with route handlers

**After:** Isolated in `app/services/scopus_service.py`

```python
class ScopusService:
    def search_papers(self, query, limit, ...):
        # All logic here
        ...
```

---

## API Endpoints (No Changes!)

All endpoints work the same way - no breaking changes!

✅ `POST /api/search`
✅ `GET /api/quick-search`
✅ `POST /api/stats`
✅ `POST /api/export/{format}`
✅ `GET /api/author/{name}`
✅ `GET /api/affiliation/{institution}`
✅ `GET /api/highly-cited`
✅ `GET /api/pdf-link/{doi}`
✅ `GET /api/download-info/{eid}`
✅ `GET /health`

---

## Benefits

### 🎯 Maintainability

- Each module has single responsibility
- Easy to find and fix bugs
- Clear separation of concerns

### 🧪 Testability

- Services can be tested independently
- Easy to mock dependencies
- Better unit test coverage

### 🚀 Scalability

- Easy to add new features
- Can add caching, rate limiting, etc.
- Ready for microservices if needed

### 🔒 Security

- API keys in environment variables
- Better secrets management
- Config per environment

### 📚 Code Quality

- Type hints everywhere
- Pydantic validation
- Clear interfaces

---

## Next Steps (Optional)

### Add Caching

```python
# In app/services/scopus_service.py
from functools import lru_cache

@lru_cache(maxsize=100)
def search(self, query, ...):
    ...
```

### Add Rate Limiting

```python
# Install: pip install slowapi
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/search")
@limiter.limit("10/minute")
async def search_papers(...):
    ...
```

### Add Database

```python
# app/db/database.py
from sqlalchemy import create_engine

engine = create_engine("sqlite:///./scopus.db")
```

### Add Tests

```python
# tests/test_search.py
def test_search_endpoint():
    response = client.post("/api/search", json={
        "query": "test",
        "limit": 10
    })
    assert response.status_code == 200
```

### Docker Support

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run.py"]
```

---

## Troubleshooting

### Import Error: pydantic_settings

```bash
pip install pydantic-settings
```

### Config not loading

Check `.env` file exists and has correct format

### Old endpoints not working

Make sure you're running `python run.py` (new entry point)

---

**🎉 Congratulations! Your API is now production-ready!**
