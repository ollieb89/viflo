# PostgreSQL Setup Template

> Minimal PostgreSQL setup for local development with Docker

## Quick Start

```bash
# Copy environment file
cp .env.example .env

# Start PostgreSQL
docker-compose up -d postgres

# Verify connection
docker-compose exec postgres pg_isready
```

## Usage

### With PgAdmin (optional)

```bash
docker-compose --profile tools up -d
```

Access PgAdmin at http://localhost:5050

### Connection Details

| Setting | Value |
|---------|-------|
| Host | localhost |
| Port | 5432 |
| Database | app |
| User | postgres |
| Password | changeme (from .env) |

### SQLAlchemy Configuration

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Connection pooling setup
engine = create_engine(
    "postgresql://postgres:changeme@localhost:5432/app",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

## Extensions Enabled

- `uuid-ossp` - UUID generation
- `pg_trgm` - Trigram matching for search
- `pg_stat_statements` - Query statistics

## Performance Tuning

The PostgreSQL configuration includes optimizations for development:
- Shared buffers: 256MB
- Work memory: 8MB
- Effective cache size: 768MB

Adjust in `docker-compose.yml` for production workloads.
