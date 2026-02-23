# Docker Compose Patterns

> Common patterns for Docker Compose configurations

## Development vs Production

### Development (docker-compose.yml)

```yaml
version: "3.8"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - .:/app # Mount for hot reload
      - /app/node_modules # Anonymous volume (don't overwrite)
    environment:
      - DEBUG=1
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/dev
    depends_on:
      - db
    command: npm run dev # Development server

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Production (docker-compose.prod.yml)

```yaml
version: "3.8"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DEBUG=0
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/prod
    depends_on:
      - db
    restart: always
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
      POSTGRES_DB: prod
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always
    secrets:
      - db_password

volumes:
  postgres_data:

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

Run with: `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d`

## Environment Variables

### .env File

```bash
# .env
COMPOSE_PROJECT_NAME=myapp
DATABASE_URL=postgresql://postgres:postgres@db:5432/app
REDIS_URL=redis://redis:6379
DEBUG=1
```

### Variable Interpolation

```yaml
services:
  app:
    image: myapp:${VERSION:-latest}
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - DEBUG=${DEBUG:-0}
    ports:
      - "${APP_PORT:-8000}:8000"
```

## Health Checks

```yaml
services:
  app:
    build: .
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
```

## Network Configuration

### Custom Network

```yaml
services:
  frontend:
    build: ./frontend
    networks:
      - frontend_network

  backend:
    build: ./backend
    networks:
      - frontend_network
      - backend_network

  db:
    image: postgres:16
    networks:
      - backend_network

networks:
  frontend_network:
    driver: bridge
  backend_network:
    driver: bridge
    internal: true # No external access
```

## Volume Management

### Named Volumes

```yaml
services:
  app:
    build: .
    volumes:
      - app_data:/app/data
      - /app/temp # Anonymous volume (ephemeral)

  db:
    image: postgres:16
    volumes:
      - type: volume
        source: postgres_data
        target: /var/lib/postgresql/data
        volume:
          nocopy: true

volumes:
  app_data:
    driver: local
  postgres_data:
    driver: local
```

### Bind Mounts (Development)

```yaml
services:
  app:
    build: .
    volumes:
      - type: bind
        source: .
        target: /app
      - type: volume
        source: node_modules
        target: /app/node_modules

volumes:
  node_modules:
```

## Scaling Services

```yaml
services:
  app:
    build: .
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: "0.5"
          memory: 256M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - app
```

Run: `docker-compose up -d --scale app=3`

## Secrets Management

```yaml
services:
  app:
    build: .
    secrets:
      - api_key
      - db_password
    environment:
      - API_KEY_FILE=/run/secrets/api_key

secrets:
  api_key:
    file: ./secrets/api_key.txt
  db_password:
    file: ./secrets/db_password.txt
```

## Profiles (Conditional Services)

```yaml
services:
  app:
    build: .

  pgadmin:
    image: dpage/pgadmin4
    profiles:
      - tools # Only started with --profile tools

  mailhog:
    image: mailhog/mailhog
    profiles:
      - dev
      - tools
```

Run: `docker-compose --profile tools up -d`

## Init Containers

```yaml
services:
  migrate:
    build: .
    command: alembic upgrade head
    depends_on:
      db:
        condition: service_healthy
    profiles:
      - migrate

  app:
    build: .
    depends_on:
      - migrate
```

## Common Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f app

# Scale service
docker-compose up -d --scale app=3

# Run one-time command
docker-compose run --rm app python manage.py migrate

# Build and start
docker-compose up -d --build

# Down (remove containers and networks)
docker-compose down

# Down with volumes (⚠️ data loss)
docker-compose down -v

# Execute command in running container
docker-compose exec app bash
```
