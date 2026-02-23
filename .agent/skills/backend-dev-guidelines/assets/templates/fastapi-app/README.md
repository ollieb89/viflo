# FastAPI Application Template

> Minimal FastAPI starter with SQLAlchemy 2.0, Pydantic v2, and PostgreSQL

## Quick Start

### Using Docker (Recommended)

```bash
# Start services
docker-compose up -d

# Run migrations
docker-compose exec app alembic revision --autogenerate -m "initial"
docker-compose exec app alembic upgrade head

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database (PostgreSQL must be running)
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/app"

# Run migrations
alembic upgrade head

# Start server
uvicorn main:app --reload
```

## Project Structure

```
app/
├── api/
│   ├── deps.py          # Dependencies (db, auth)
│   └── v1/
│       ├── endpoints/   # API endpoints
│       └── router.py    # v1 router
├── core/
│   ├── config.py        # Settings
│   └── security.py      # JWT, password hashing
├── db/
│   └── base.py          # SQLAlchemy base, session
├── models/              # Database models
├── repositories/        # Repository pattern
│   └── base.py
└── schemas/             # Pydantic schemas
```

## Creating New Endpoints

Use the generator:

```bash
python .agent/skills/backend-dev-guidelines/scripts/generate-endpoint.py Product \
    --fields "name:str,price:float,active:bool"
```

Or manually:

1. Create schema in `app/schemas/product.py`
2. Create model in `app/models/product.py`
3. Create repository in `app/repositories/product.py`
4. Create router in `app/api/v1/endpoints/product.py`
5. Add to `app/api/v1/router.py`
6. Create migration: `alembic revision --autogenerate -m "add product"`

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=term-missing
```

## Environment Variables

| Variable                    | Default          | Description         |
| --------------------------- | ---------------- | ------------------- |
| DATABASE_URL                | postgresql://... | Database connection |
| SECRET_KEY                  | change-me        | JWT signing key     |
| ACCESS_TOKEN_EXPIRE_MINUTES | 1440             | Token expiry        |
| ALLOWED_HOSTS               | \*               | CORS origins        |

## Learn More

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/)
- [Pydantic v2](https://docs.pydantic.dev/)
