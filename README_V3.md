# 🎉 Scopus Search API v3.0 - Complete Guide

## ✨ New Features

### 1. **User Authentication** 🔐

- Register dengan email & password
- Login dengan JWT tokens
- Secure password hashing

### 2. **Personal API Keys** 🔑

- Input Scopus API key sendiri
- Manage multiple API keys
- Encrypted storage di database

### 3. **Wishlist** ⭐

- Save favorite papers
- Add personal notes
- Easy management

### 4. **Redis Caching** ⚡

- Cache search results
- Faster response time
- Reduced API calls

### 5. **PostgreSQL Database** 💾

- User data storage
- API key management
- Wishlist persistence

---

## 🏃 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Database & Redis

**Local Development:**

```bash
# Install PostgreSQL
# Install Redis

# Or use Docker:
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres
docker run -d -p 6379:6379 redis
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/scopus_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=generate-with-secrets-module
ENCRYPTION_KEY=generate-with-secrets-module
```

Generate keys:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Run Server

```bash
python run.py
```

Access at: http://localhost:8000

---

## 📚 API Documentation

### Authentication Endpoints

#### Register

```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

#### Login

```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "yourpassword"
}

# Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "is_active": true
  }
}
```

#### Get Current User

```bash
GET /api/auth/me
Authorization: Bearer <token>
```

---

### API Key Management

#### Add API Key

```bash
POST /api/keys/
Authorization: Bearer <token>
Content-Type: application/json

{
  "key_name": "My Scopus Key",
  "api_key": "73439d14c6dc73b3a06756cbc9de5a4a"
}
```

#### List API Keys

```bash
GET /api/keys/
Authorization: Bearer <token>
```

#### Get Active Key (for API calls)

```bash
GET /api/keys/active
Authorization: Bearer <token>
```

#### Delete API Key

```bash
DELETE /api/keys/{key_id}
Authorization: Bearer <token>
```

---

### Wishlist Endpoints

#### Add to Wishlist

```bash
POST /api/wishlist/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Paper Title",
  "authors": "Author Name",
  "year": "2023",
  "publication": "Journal Name",
  "cited_by": 50,
  "doi": "10.1234/example",
  "eid": "2-s2.0-xxxxx",
  "scopus_url": "https://...",
  "notes": "Interesting paper about..."
}
```

#### Get Wishlist

```bash
GET /api/wishlist/
Authorization: Bearer <token>
```

#### Delete from Wishlist

```bash
DELETE /api/wishlist/{item_id}
Authorization: Bearer <token>
```

#### Update Notes

```bash
PATCH /api/wishlist/{item_id}/notes?notes=New notes here
Authorization: Bearer <token>
```

#### Check if in Wishlist

```bash
GET /api/wishlist/check/{eid}
Authorization: Bearer <token>
```

---

### Search Endpoints (Same as before, but now uses user's API key)

#### Search Papers

```bash
POST /api/search
Authorization: Bearer <token>  # Now required!
Content-Type: application/json

{
  "query": "machine learning",
  "limit": 50,
  "year_from": 2020
}
```

All other search, stats, export endpoints remain the same, just add `Authorization` header.

---

## 🔧 Architecture Changes

### New Structure

```
app/
├── api/
│   ├── auth.py          # ✨ NEW: Authentication
│   ├── apikeys.py       # ✨ NEW: API key management
│   ├── wishlist.py      # ✨ NEW: Wishlist
│   ├── search.py        # Updated with auth
│   └── ...
├── db/                  # ✨ NEW: Database
│   ├── database.py
│   └── models.py        # User, ApiKey, Wishlist
├── core/
│   ├── security.py      # ✨ NEW: JWT, encryption
│   ├── dependencies.py  # Updated with auth
│   └── config.py        # Updated with new settings
├── schemas/
│   └── auth.py          # ✨ NEW: Auth schemas
└── services/
    ├── redis_service.py # ✨ NEW: Redis caching
    └── scopus_service.py # Updated with caching
```

---

## 🔐 Security Features

### 1. Password Hashing

- Uses bcrypt for secure password storage
- Never stores plain passwords

### 2. JWT Tokens

- Secure token-based authentication
- Configurable expiration time
- Bearer token in Authorization header

### 3. API Key Encryption

- User API keys encrypted in database
- Uses Fernet symmetric encryption
- Never exposed in responses

### 4. Environment Variables

- Sensitive data in .env
- Not committed to git
- Different per environment

---

## 📊 Database Schema

### Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### API Keys Table

```sql
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    key_name VARCHAR(100) NOT NULL,
    api_key VARCHAR(255) NOT NULL,  -- Encrypted
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Wishlist Table

```sql
CREATE TABLE wishlists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(500) NOT NULL,
    authors VARCHAR(500),
    year VARCHAR(10),
    publication VARCHAR(300),
    cited_by INTEGER DEFAULT 0,
    doi VARCHAR(100),
    eid VARCHAR(100),
    scopus_url TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🚀 Deploy to Heroku

See [HEROKU_DEPLOY.md](HEROKU_DEPLOY.md) for detailed instructions.

Quick version:

```bash
# Create app
heroku create your-app-name

# Add PostgreSQL & Redis
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini

# Set environment variables
heroku config:set SECRET_KEY="..."
heroku config:set ENCRYPTION_KEY="..."

# Deploy
git push heroku main

# Initialize database
heroku run python -c "from app.db import init_db; init_db()"
```

---

## 🧪 Testing

### Register & Login

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Save token
TOKEN="<your-token-here>"
```

### Add API Key

```bash
curl -X POST http://localhost:8000/api/keys/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"key_name":"My Key","api_key":"your-scopus-key"}'
```

### Search

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"machine learning","limit":10}'
```

### Add to Wishlist

```bash
curl -X POST http://localhost:8000/api/wishlist/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Paper","eid":"2-s2.0-123"}'
```

---

## 💡 Tips & Best Practices

### 1. Token Management

- Store token in localStorage/sessionStorage
- Include in all API requests
- Handle token expiration

### 2. API Key Security

- Never expose API keys in client-side code
- Use environment variables
- Rotate keys regularly

### 3. Caching

- Redis cache expires after 1 hour
- Clear cache when needed
- Monitor cache hit rate

### 4. Database

- Regular backups
- Monitor connections
- Use connection pooling

---

## 📈 Monitoring

### Health Check

```bash
GET /health
```

### Check Database

```bash
heroku pg:info
```

### Check Redis

```bash
heroku redis:info
```

### View Logs

```bash
heroku logs --tail
```

---

## 🔄 Migration from v2.0

1. **Install new dependencies**

```bash
pip install -r requirements.txt
```

2. **Setup database & Redis**

```bash
# Local or Heroku
```

3. **Run migrations**

```bash
python -c "from app.db import init_db; init_db()"
```

4. **Update frontend** (see next section)

5. **Test all endpoints**

---

## 🎨 Frontend Integration

The API now requires authentication for most endpoints. Update your frontend:

1. **Add login/register forms**
2. **Store JWT token**
3. **Include token in requests**
4. **Add API key management UI**
5. **Add wishlist UI**

See `static/index.html` for updated interface (coming next).

---

## 📞 Support

For issues or questions:

1. Check documentation
2. Review error logs
3. Check Heroku status
4. Create GitHub issue

---

**🎉 Enjoy your enhanced Scopus Search API!**

Version: 3.0.0  
Date: October 14, 2025
