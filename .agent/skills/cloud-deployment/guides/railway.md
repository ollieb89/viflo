# Railway Deployment Guide

> Deploy full-stack applications with databases to Railway

## Quick Start

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

## Project Setup

### 1. Create Project

```bash
# Create new project
railway init

# Or via dashboard
# railway.app/new
```

### 2. Add Database

```bash
# Add PostgreSQL
railway add --database postgres

# Or in dashboard:
# New → Database → PostgreSQL
```

### 3. Deploy

```bash
# Deploy from current directory
railway up

# Deploy specific directory
railway up --service backend
```

## Full-Stack Deployment

### Backend (FastAPI)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```python
# main.py
import os
from fastapi import FastAPI

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

@app.get("/")
def read_root():
    return {"status": "ok"}
```

### Frontend (Next.js)

```dockerfile
# Dockerfile
FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

### Monorepo Setup

```yaml
# railway.yml
services:
  backend:
    build:
      dockerfile: backend/Dockerfile
    ports:
      - 8000
    
  frontend:
    build:
      dockerfile: frontend/Dockerfile
    ports:
      - 3000
```

## Environment Variables

### Set Variables

```bash
# Set for all environments
railway variables set DATABASE_URL=postgresql://...

# Set in dashboard:
# Variables → Add Variable
```

### Reference Variables

```bash
# Reference other service variables
railway variables set API_URL=${{backend.PORT}}
```

### From .env File

```bash
# Load from .env
railway variables --file .env
```

## Custom Domain

### Step 1: Add Domain

Dashboard → Service → Settings → Domains → Add

### Step 2: Configure DNS

```
Type: CNAME
Name: www
Value: [provided-by-railway].railway.app
```

### Step 3: SSL

SSL auto-provisioned. Shows in dashboard.

## Database

### PostgreSQL

```bash
# Add database
railway add --database postgres

# Get connection URL
echo $DATABASE_URL
# postgresql://postgres:password@containers.railway.app:5432/railway
```

### Redis

```bash
railway add --database redis
```

### MongoDB

```bash
railway add --database mongodb
```

## Health Checks

```dockerfile
# Dockerfile with health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1
```

## Monitoring

### Logs

```bash
# View logs
railway logs

# Follow logs
railway logs --follow
```

### Metrics

Dashboard → Service → Metrics

- CPU usage
- Memory usage
- Network
- Disk

## Scaling

### Vertical

Dashboard → Service → Settings → Change Plan

### Horizontal

Not directly supported. Use multiple services.

## Pricing

| Plan | Cost | Includes |
|------|------|----------|
| Starter | Free | $5/mo credit |
| Hobby | $5/mo | 2 vCPU, 2GB RAM |
| Pro | $50/mo | 4 vCPU, 8GB RAM |

## Best Practices

1. **Use environment variables**: For all configuration
2. **Health checks**: Ensure fast startup
3. **Database migrations**: Run on deploy
4. **Logs**: Use structured logging
5. **Backups**: Enable for production databases

## Troubleshooting

### Deployment Failed

```bash
# Check logs
railway logs

# Redeploy
railway up --detach
```

### Database Connection

```bash
# Connect locally
railway connect postgres

# Run psql
\dt  # List tables
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Out of memory | Upgrade plan |
| Build fails | Check Dockerfile |
| Database connection | Verify DATABASE_URL |
