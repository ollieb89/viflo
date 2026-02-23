---
name: containerization
description: |
  Docker containerization best practices. Multi-stage builds, image optimization,
  security hardening, and production deployment patterns. Use when creating
  Dockerfiles, optimizing images, or containerizing applications.
triggers:
  - Creating Dockerfile
  - Containerizing application
  - Optimizing image size
  - Docker Compose setup
  - Production deployment
---

# Containerization

> **Docker best practices for production applications**

## Quick Start

### Generate Dockerfile

```bash
python .agent/skills/containerization/scripts/generate-dockerfile.py \
    --type python --output .
```

Types: `python`, `node`, `nextjs`, `go`

### Build and Run

```bash
# Build
docker build -t myapp:latest .

# Run
docker run -p 8000:8000 myapp:latest

# Compose
docker-compose up -d
```

---

## Multi-Stage Builds

### Python Example

```dockerfile
# Stage 1: Build
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "main.py"]
```

### Node.js Example

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Stage 2: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: Production
FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package.json ./
CMD ["node", "dist/index.js"]
```

---

## Security Best Practices

### Non-Root User

```dockerfile
# Create user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
USER appuser
```

### Minimal Base Images

| Language | Base Image                | Size  |
| -------- | ------------------------- | ----- |
| Python   | `python:3.11-slim`        | ~50MB |
| Node.js  | `node:20-alpine`          | ~40MB |
| Go       | `scratch` or `distroless` | ~5MB  |

### Secrets Handling

```dockerfile
# ❌ Don't do this
ENV API_KEY=hardcoded_secret

# ✅ Do this
ARG API_KEY
ENV API_KEY=$API_KEY
```

---

## Optimization

### Layer Caching

```dockerfile
# Good: Copy requirements first (cached unless changed)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Then copy code (changes frequently)
COPY . .
```

### Image Size Reduction

1. Use `.dockerignore`
2. Multi-stage builds
3. Minimal base images
4. Clean up cache

```dockerfile
# Clean up
RUN apt-get update && apt-get install -y \
    some-package \
    && rm -rf /var/lib/apt/lists/*
```

---

## Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

---

## Docker Compose Patterns

### Development vs Production

```yaml
# docker-compose.yml (development)
version: '3.8'
services:
  app:
    build: .
    volumes:
      - .:/app  # Mount for hot reload
    environment:
      - DEBUG=1

# docker-compose.prod.yml (production)
version: '3.8'
services:
  app:
    build: .
    restart: always
    environment:
      - DEBUG=0
```

Run with: `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up`

---

## Production Checklist

Before deploying:

- [ ] Non-root user configured
- [ ] Minimal base image used
- [ ] No secrets in image
- [ ] Health check defined
- [ ] Resource limits set
- [ ] Proper logging
- [ ] Graceful shutdown handling

---

## References

| File                                                                | Description                  |
| ------------------------------------------------------------------- | ---------------------------- |
| [docker-best-practices.md](references/docker-best-practices.md)     | Comprehensive best practices |
| [multi-stage-builds.md](references/multi-stage-builds.md)           | Language-specific examples   |
| [docker-compose-patterns.md](references/docker-compose-patterns.md) | Common patterns              |
| [production-checklist.md](references/production-checklist.md)       | Deployment verification      |

---

## Generator

```bash
# Generate optimized Dockerfile
python scripts/generate-dockerfile.py --type python --output .

# With custom port
python scripts/generate-dockerfile.py --type node --port 3000 --output .
```

---

## Anti-Patterns

❌ **Latest tag**: Use specific versions (`python:3.11` not `python:latest`)  
❌ **Multiple RUNs**: Combine commands to reduce layers  
❌ **Large context**: Use `.dockerignore`  
❌ **Root user**: Always use non-root when possible  
❌ **Secrets in image**: Use environment variables  
❌ **No health check**: Always define health checks
