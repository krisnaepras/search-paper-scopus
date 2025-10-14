# 🚀 Scopus Search API v3.0 - Deploy ke Heroku

## Prerequisites

- Akun Heroku
- Heroku CLI installed
- Git initialized

## Setup Heroku

### 1. Create Heroku App

```bash
heroku create scopus-search-api
```

### 2. Add PostgreSQL

```bash
heroku addons:create heroku-postgresql:mini
```

### 3. Add Redis

```bash
heroku addons:create heroku-redis:mini
```

### 4. Set Environment Variables

```bash
# Generate secret keys
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set environment variables
heroku config:set SECRET_KEY="your-generated-secret-key"
heroku config:set ENCRYPTION_KEY="your-generated-encryption-key"
heroku config:set SCOPUS_API_KEY="your-default-scopus-api-key"
heroku config:set DEBUG=False
```

### 5. Deploy

```bash
git add .
git commit -m "Deploy v3.0"
git push heroku main
```

### 6. Run Migrations

```bash
heroku run python -c "from app.db import init_db; init_db()"
```

### 7. Open App

```bash
heroku open
```

## Environment Variables (Heroku Auto-Set)

- `DATABASE_URL` - PostgreSQL URL (auto-set by Heroku)
- `REDIS_URL` - Redis URL (auto-set by Heroku)
- `PORT` - Port number (auto-set by Heroku)

## Manual Configuration Needed

```bash
heroku config:set SECRET_KEY="..."
heroku config:set ENCRYPTION_KEY="..."
heroku config:set SCOPUS_API_KEY="..." # Optional default
```

## View Logs

```bash
heroku logs --tail
```

## Scale Dynos

```bash
heroku ps:scale web=1
```

## Database Management

```bash
# Connect to database
heroku pg:psql

# Backup database
heroku pg:backups:capture
heroku pg:backups:download
```

## Redis Management

```bash
# View Redis info
heroku redis:info

# Clear Redis cache
heroku redis:cli
> FLUSHDB
```

## Useful Commands

```bash
# Restart app
heroku restart

# Open logs
heroku logs --tail

# Run bash
heroku run bash

# Check config
heroku config
```

## Cost Estimate

- Hobby dyno: $7/month
- PostgreSQL Mini: $5/month
- Redis Mini: $3/month
  **Total: ~$15/month**

Free tier also available (limited hours).
