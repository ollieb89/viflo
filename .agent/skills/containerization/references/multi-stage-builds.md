# Multi-Stage Build Examples

> Language-specific multi-stage build patterns for production optimization

## Overview

Multi-stage builds allow you to use one base image for building and a smaller image for production, significantly reducing final image size.

## Python

### Standard Pattern

```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Production
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application
COPY . .

USER appuser

EXPOSE 8000
CMD ["python", "main.py"]
```

**Size reduction**: ~900MB → ~100MB

### With Poetry

```dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy only installed packages
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

CMD ["python", "main.py"]
```

## Node.js

### Standard Pattern

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

ENV NODE_ENV=production

# Create user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Copy only necessary files
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package.json ./

USER nextjs

EXPOSE 3000
CMD ["node", "dist/index.js"]
```

**Size reduction**: ~1.5GB → ~200MB

### Next.js Specific

```dockerfile
# Dependencies
FROM node:20-alpine AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Copy standalone output (requires output: 'standalone' in next.config.js)
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000

CMD ["node", "server.js"]
```

## Go

### Standard Pattern

```dockerfile
# Stage 1: Build
FROM golang:1.21-alpine AS builder

WORKDIR /app

# Install git for modules
RUN apk add --no-cache git

# Copy and download dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy source
COPY . .

# Build binary
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# Stage 2: Minimal runtime
FROM gcr.io/distroless/static:nonroot

WORKDIR /

# Copy binary
COPY --from=builder /app/main .

# Use nonroot user (65532:65532)
USER 65532:65532

EXPOSE 8080

CMD ["/main"]
```

**Size reduction**: ~1GB → ~10MB

### With Alpine (if you need shell)

```dockerfile
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o main .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/main .
CMD ["./main"]
```

## Rust

```dockerfile
# Stage 1: Build
FROM rust:1.75-slim as builder

WORKDIR /app

# Copy manifests
COPY Cargo.toml Cargo.lock ./

# Build dependencies (cached layer)
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo build --release
RUN rm -rf src

# Copy source and build
COPY . .
RUN cargo build --release

# Stage 2: Runtime
FROM debian:bookworm-slim

WORKDIR /app

# Copy binary
COPY --from=builder /app/target/release/myapp .

# Create user
RUN useradd -m appuser
USER appuser

EXPOSE 8080
CMD ["./myapp"]
```

## Java

```dockerfile
# Stage 1: Build
FROM maven:3.9-eclipse-temurin-21-alpine AS builder

WORKDIR /app

COPY pom.xml .
RUN mvn dependency:go-offline

COPY src ./src
RUN mvn package -DskipTests

# Stage 2: Runtime
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

COPY --from=builder /app/target/*.jar app.jar

EXPOSE 8080
CMD ["java", "-jar", "app.jar"]
```

## Benefits Summary

| Language | Single Stage | Multi-Stage | Reduction |
| -------- | ------------ | ----------- | --------- |
| Python   | ~900MB       | ~100MB      | 89%       |
| Node.js  | ~1.5GB       | ~200MB      | 87%       |
| Go       | ~1GB         | ~10MB       | 99%       |
| Rust     | ~2GB         | ~50MB       | 98%       |
| Java     | ~500MB       | ~150MB      | 70%       |

## Best Practices

1. **Use specific stage names**: `FROM node:20 AS builder` not just `FROM node:20`
2. **Only copy what's needed**: Don't copy build tools to production
3. **Cache dependencies**: Copy package files before source code
4. **Minimize layers**: Combine commands where appropriate
5. **Use non-root users**: Always in final stage
6. **Health checks**: Define in final stage only
