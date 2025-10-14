# 🚀 Scopus Search API - Improved Architecture

REST API untuk mencari paper di Scopus dengan **arsitektur yang bersih dan efisien**.

**Framework:** FastAPI dengan Clean Architecture Pattern

---

## 📂 Project Structure (NEW!)

```
web-search-scopus/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── api/                    # API routes (controllers)
│   │   ├── __init__.py
│   │   ├── search.py          # Search endpoints
│   │   ├── stats.py           # Statistics endpoints
│   │   ├── export.py          # Export endpoints
│   │   ├── author.py          # Author/affiliation endpoints
│   │   ├── download.py        # Download info endpoints
│   │   └── health.py          # Health check endpoints
│   ├── core/                   # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py          # Settings & configuration
│   │   └── dependencies.py    # Dependency injection
│   ├── schemas/                # Pydantic models
│   │   ├── __init__.py
│   │   ├── enums.py           # Enums
│   │   ├── paper.py           # Paper models
│   │   ├── search.py          # Search models
│   │   └── stats.py           # Statistics models
│   └── services/               # Business logic
│       ├── __init__.py
│       └── scopus_service.py  # Scopus API service
├── static/
│   └── index.html             # Web interface
├── .env.example               # Environment variables template
├── .gitignore
├── requirements.txt           # Python dependencies
├── run.py                     # Application entry point
└── README.md
```

---

## ✨ Architecture Improvements

### 1. **Separation of Concerns**

- **Routes (Controllers)**: Thin layer, hanya handle HTTP request/response
- **Services**: Business logic dan Scopus API interactions
- **Schemas**: Data validation menggunakan Pydantic
- **Config**: Centralized configuration management

### 2. **Configuration Management**

- Environment variables support via `.env` file
- Type-safe settings menggunakan `pydantic-settings`
- Easy to override values per environment

### 3. **Modular Routes**

- Setiap endpoint group di file terpisah
- Lebih mudah di-maintain dan test
- Clear responsibility untuk setiap module

### 4. **Service Layer**

- All Scopus API logic di satu tempat
- Reusable business logic
- Easy to mock untuk testing

### 5. **Better Error Handling**

- Global exception handlers
- Consistent error responses
- Proper HTTP status codes

---

## 📦 Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

---

## ⚙️ Configuration

1. Copy `.env.example` ke `.env`:

```bash
cp .env.example .env
```

2. Edit `.env` dan isi dengan API key Anda:

```env
SCOPUS_API_KEY=your_actual_api_key_here
DEBUG=True  # Set to False in production
```

---

## 🏃 Run Server

### Method 1: Using run.py (Recommended)

```bash
python run.py
```

### Method 2: Using uvicorn directly

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server akan running di: **http://localhost:8000**

---

## 📖 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Web Interface**: http://localhost:8000

---

## 🎯 API Endpoints

### Search

- `POST /api/search` - Full search dengan filters
- `GET /api/quick-search` - Quick search (GET method)
- `GET /api/highly-cited` - Highly cited papers

### Statistics

- `POST /api/stats` - Statistical analysis

### Export

- `POST /api/export/{format}` - Export to JSON/CSV/Excel

### Author & Affiliation

- `GET /api/author/{name}` - Search by author
- `GET /api/affiliation/{institution}` - Search by institution

### Download

- `GET /api/pdf-link/{doi}` - Get PDF links
- `GET /api/download-info/{eid}` - Download options

### Health

- `GET /health` - Health check
- `GET /api` - API info

---

## 🔧 Development Tips

### Add New Endpoint

1. Create route in `app/api/`
2. Register router in `app/main.py`
3. Add business logic in `app/services/` if needed

### Add New Configuration

1. Add field to `Settings` class in `app/core/config.py`
2. Add to `.env.example`

### Testing

```bash
# Run with debug mode
# Set DEBUG=True in .env

# Check health
curl http://localhost:8000/health

# Test search
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "limit": 10}'
```

---

## 📊 Key Improvements Summary

| Aspect          | Before               | After                            |
| --------------- | -------------------- | -------------------------------- |
| File Structure  | Single 677-line file | Modular structure with 15+ files |
| Configuration   | Hard-coded           | Environment variables + Pydantic |
| Routes          | All in one file      | Separated by concern             |
| Business Logic  | Mixed with routes    | Isolated in service layer        |
| Models          | In main file         | Separate schemas module          |
| Reusability     | Low                  | High                             |
| Testability     | Hard                 | Easy                             |
| Maintainability | Difficult            | Excellent                        |

---

## 🚀 Performance Features

- **Efficient pagination**: Smart multi-page fetching
- **Request caching**: Reduce redundant API calls
- **Async support**: FastAPI's async capabilities
- **Streaming responses**: For large exports
- **Connection pooling**: HTTP session management

---

## 📝 Notes

- Old `api_scopus.py` is preserved for reference
- New architecture follows FastAPI best practices
- Easy to add features like caching, rate limiting, etc.
- Ready for Docker deployment
- Can easily add database support if needed

---

## 🔒 Security Best Practices

- API keys in environment variables (not in code)
- CORS configuration
- Input validation via Pydantic
- Error message sanitization in production

---

**Made with ❤️ using FastAPI and Clean Architecture principles**
