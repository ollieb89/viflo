# Docker Best Practices

> Guidelines for building secure, efficient Docker images

## Layer Caching

Docker builds images in layers. Each instruction creates a new layer. Optimize by ordering instructions from least to most frequently changing.

### Good Ordering

```dockerfile
# 1. Base image (rarely changes)
FROM python:3.11-slim

# 2. System dependencies (rarely changes)
RUN apt-get update && apt-get install -y gcc

# 3. Application dependencies (changes occasionally)
COPY requirements.txt .
RUN pip install -r requirements.txt

# 4. Application code (changes frequently)
COPY . .
```

### Bad Ordering

```dockerfile
# ❌ Don't copy code before dependencies
COPY . .
RUN pip install -r requirements.txt
```

## Image Size Optimization

### 1. Use Minimal Base Images

| Image | Size | Use Case |
|-------|------|----------|
| `python:3.11` | ~900MB | Development |
| `python:3.11-slim` | ~50MB | Production |
| `python:3.11-alpine` | ~20MB | Minimal |
| `distroless` | ~5MB | Go/Rust |

### 2. Multi-Stage Builds

```dockerfile
# Build stage
FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage (smaller)
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

### 3. Clean Up

```dockerfile
# Good: Clean up in same layer
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Bad: Leaves cache in separate layer
RUN apt-get update
RUN apt-get install -y build-essential
```

## Security

### Non-Root User

```dockerfile
# Create user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Set ownership
RUN chown -R appuser:appgroup /app
USER appuser
```

### Secrets Handling

```dockerfile
# ❌ Bad: Hardcoded secret
ENV API_KEY=abc123

# ✅ Good: Build argument
ARG API_KEY
ENV API_KEY=$API_KEY

# Build with: docker build --build-arg API_KEY=secret .
```

### Read-Only Filesystems

```dockerfile
# Make filesystem read-only
RUN chmod -R 555 /app

# Or at runtime
docker run --read-only myapp
```

## .dockerignore

Always use `.dockerignore` to reduce build context size.

```
# Git
.git
.gitignore

# Python
__pycache__/
*.pyc
.venv/
venv/

# Node.js
node_modules/
npm-debug.log

# IDE
.idea/
.vscode/

# OS
.DS_Store
Thumbs.db

# Testing
.coverage
.pytest_cache/
```

## Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

Options:
- `--interval`: Check frequency (default: 30s)
- `--timeout`: Check timeout (default: 30s)
- `--start-period`: Grace period for slow-starting containers
- `--retries`: Consecutive failures before unhealthy

## Environment Variables

### Build-time vs Runtime

```dockerfile
# ARG: Build-time only
ARG VERSION=1.0.0
RUN echo "Building version $VERSION"

# ENV: Runtime available
ENV NODE_ENV=production
ENV PORT=8000
```

### Required Variables

```dockerfile
# Fail fast if required env var not set
ENV DATABASE_URL=${DATABASE_URL:?DATABASE_URL is required}
```

## Resource Limits

Always set resource constraints:

```bash
docker run \
  --memory="512m" \
  --memory-swap="1g" \
  --cpus="1.0" \
  myapp
```

In Compose:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
```

## Logging

### JSON Logging (structured)

```dockerfile
# Configure app to log JSON
ENV LOG_FORMAT=json
```

### Log Rotation

```bash
docker run \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  myapp
```

## Common Mistakes

### 1. Using `latest` Tag

```dockerfile
# ❌ Bad: Non-deterministic
FROM node:latest

# ✅ Good: Version pinned
FROM node:20.11.0-alpine
```

### 2. Running as Root

```dockerfile
# ❌ Bad: Security risk
# (no USER instruction)

# ✅ Good: Non-root user
RUN useradd -m myuser
USER myuser
```

### 3. Exposing Unnecessary Ports

```dockerfile
# ❌ Bad: Expose only what's needed
EXPOSE 8000 9000 3000

# ✅ Good: Minimal exposure
EXPOSE 8000
```

### 4. Not Handling Signals

```dockerfile
# Use exec form for proper signal handling
CMD ["python", "main.py"]

# Not shell form (creates subshell)
# CMD python main.py
```

## Build Optimization Checklist

- [ ] `.dockerignore` configured
- [ ] Minimal base image used
- [ ] Multi-stage build implemented
- [ ] Layers ordered by change frequency
- [ ] No unnecessary packages installed
- [ ] Cache cleaned up
- [ ] Non-root user configured
- [ ] Health check defined
- [ ] Resource limits set
- [ ] Image size < 200MB (for microservices)
