# ⚡ Quick Start Guide - New Architecture

## 🚀 Get Started in 3 Steps

### Step 1: Setup

```bash
# Windows
setup.bat

# Linux/Mac
chmod +x setup.sh && ./setup.sh
```

### Step 2: Configure

Edit `.env` file:

```env
SCOPUS_API_KEY=73439d14c6dc73b3a06756cbc9de5a4a
DEBUG=True
```

### Step 3: Run

```bash
python run.py
```

**That's it!** 🎉 Visit http://localhost:8000

---

## 📊 Before vs After

### File Structure

```
BEFORE                          AFTER
─────────────────────────────────────────────────
api_scopus.py (677 lines)      app/
                                ├── api/ (6 files)
                                ├── core/ (2 files)
                                ├── schemas/ (5 files)
                                └── services/ (1 file)
```

### Code Organization

```
BEFORE: Everything Mixed        AFTER: Clean Separation
─────────────────────────────────────────────────
• Imports                       • Routes → app/api/
• Config                        • Config → app/core/
• Models                        • Models → app/schemas/
• Business logic                • Logic → app/services/
• Error handling
• Server setup
```

### Configuration

```
BEFORE                          AFTER
─────────────────────────────────────────────────
Hard-coded in file:             .env file:
API_KEY = "xxx"                 SCOPUS_API_KEY=xxx
                                DEBUG=True
                                MAX_RESULTS=1000
```

---

## 🎯 What Changed?

### ✅ Added

- Environment variable support
- Modular route structure
- Service layer for business logic
- Pydantic schemas for validation
- Dependency injection
- Better error handling
- Comprehensive documentation

### ✅ Improved

- Code organization (677 lines → 20+ files)
- Maintainability (Easy to find and fix)
- Testability (Services can be tested)
- Scalability (Easy to extend)
- Security (API keys in .env)

### ✅ Kept Same

- All API endpoints work exactly the same
- Same request/response format
- Same functionality
- No breaking changes!

---

## 🔍 Compare: Old vs New Code

### Old Way (api_scopus.py)

```python
# Everything in one file
API_KEY = "73439d14c6dc73b3a06756cbc9de5a4a"  # Hard-coded!

@app.post("/api/search")
async def search_papers(request: SearchRequest):
    # 50+ lines of logic here
    full_query = build_query(...)
    entries = fetch_multiple_pages(...)
    papers = [parse_entry(entry) for entry in entries]
    return SearchResponse(...)
```

### New Way (Clean Architecture)

```python
# app/core/config.py
class Settings(BaseSettings):
    scopus_api_key: str  # From .env

# app/services/scopus_service.py
class ScopusService:
    def search_papers(...):
        # Business logic here

# app/api/search.py
@router.post("/search")
async def search_papers(request: SearchRequest):
    papers, query, total = scopus_service.search_papers(...)
    return SearchResponse(...)
```

**Result**: Clean, organized, maintainable! ✨

---

## 📁 New Project Structure

```
web-search-scopus/
│
├── 📱 app/                      # Main application
│   ├── 🌐 api/                  # API routes (controllers)
│   │   ├── search.py           # Search endpoints
│   │   ├── stats.py            # Statistics
│   │   ├── export.py           # Export
│   │   ├── author.py           # Author search
│   │   ├── download.py         # Download info
│   │   └── health.py           # Health checks
│   │
│   ├── ⚙️ core/                 # Configuration
│   │   ├── config.py           # Settings (from .env)
│   │   └── dependencies.py     # Dependency injection
│   │
│   ├── 📋 schemas/              # Data models
│   │   ├── enums.py            # Enums
│   │   ├── paper.py            # Paper model
│   │   ├── search.py           # Search models
│   │   └── stats.py            # Stats model
│   │
│   ├── 🔧 services/             # Business logic
│   │   └── scopus_service.py   # Scopus API
│   │
│   └── main.py                 # App initialization
│
├── 🌐 static/                   # Web interface
│   └── index.html
│
├── 📝 Documentation
│   ├── README_NEW.md           # Complete guide
│   ├── MIGRATION.md            # Migration guide
│   ├── ARCHITECTURE.txt        # Architecture diagram
│   └── REFACTORING_SUMMARY.md  # This summary
│
├── ⚙️ Configuration
│   ├── .env.example            # Template
│   ├── requirements.txt        # Dependencies
│   └── .gitignore
│
├── 🚀 Entry Points
│   ├── run.py                  # Start server
│   ├── setup.sh                # Setup (Linux/Mac)
│   └── setup.bat               # Setup (Windows)
│
└── 📚 Legacy
    └── api_scopus.py           # Old version (reference)
```

---

## 🎓 Key Concepts

### 1. **Layered Architecture**

```
HTTP → Routes → Schemas → Services → External API
```

### 2. **Separation of Concerns**

- **Routes**: Handle HTTP (thin layer)
- **Schemas**: Validate data
- **Services**: Business logic
- **Config**: Settings

### 3. **Single Responsibility**

Each file does ONE thing:

- `search.py` → Search routes
- `stats.py` → Statistics routes
- `scopus_service.py` → Scopus API logic

### 4. **Dependency Injection**

Services can be easily swapped or mocked:

```python
def get_scopus_service():
    yield scopus_service  # Easy to mock!
```

---

## ✨ Benefits Summary

| Benefit         | Old           | New         |
| --------------- | ------------- | ----------- |
| **Find code**   | Hard 😞       | Easy ✅     |
| **Add feature** | Risky 😰      | Safe ✅     |
| **Test code**   | Difficult 😓  | Simple ✅   |
| **Scale app**   | Limited 😐    | Ready ✅    |
| **Configure**   | Hard-coded 😖 | Flexible ✅ |
| **Collaborate** | Conflicts 😤  | Smooth ✅   |

---

## 🛠️ Common Tasks

### Add New Endpoint

```python
# 1. Create route in app/api/
@router.get("/my-endpoint")
async def my_endpoint():
    data = scopus_service.my_method()
    return data

# 2. Register in app/main.py
app.include_router(my_router)
```

### Add New Configuration

```python
# 1. Add to app/core/config.py
class Settings(BaseSettings):
    my_setting: str = "default"

# 2. Add to .env.example
MY_SETTING=value

# 3. Use anywhere
from app.core import settings
value = settings.my_setting
```

### Add Business Logic

```python
# Add to app/services/scopus_service.py
def my_new_method(self, param):
    # Logic here
    return result
```

---

## 🎯 Quick Reference

### Run Commands

```bash
# Setup (first time)
setup.bat  # or setup.sh

# Run server
python run.py

# Run with hot reload
uvicorn app.main:app --reload

# Install single package
pip install package-name
```

### URLs

- Web: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

### Important Files

- `app/main.py` - App entry point
- `app/core/config.py` - Configuration
- `app/services/scopus_service.py` - Business logic
- `.env` - Environment variables
- `run.py` - Start server

---

## ❓ FAQ

**Q: Do I need to change my API calls?**
A: No! All endpoints work exactly the same.

**Q: What happened to api_scopus.py?**
A: Still there for reference, but use the new structure.

**Q: Can I go back to the old version?**
A: Yes, just run `python api_scopus.py`

**Q: Is this production-ready?**
A: Yes! Much more production-ready than before.

**Q: How do I add caching?**
A: Add it in `app/services/scopus_service.py`

**Q: How do I add authentication?**
A: Create `app/core/security.py` and add middleware

---

## 🎉 You're Ready!

Your FastAPI application is now:

- ✅ Well-organized
- ✅ Easy to maintain
- ✅ Production-ready
- ✅ Scalable
- ✅ Testable

### Next Steps:

1. Run `python run.py`
2. Test at http://localhost:8000
3. Read `README_NEW.md` for details
4. Start building! 🚀

---

**Made with ❤️ - Happy Coding!**
