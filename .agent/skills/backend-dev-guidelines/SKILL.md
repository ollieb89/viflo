---
name: backend-dev-guidelines
description: |
  Comprehensive guide for FastAPI backend development. Use when creating APIs, 
  database models, authentication, or business logic. Covers SQLAlchemy 2.0, 
  Pydantic v2, repository pattern, and testing best practices.
triggers:
  - Creating FastAPI endpoints
  - Designing database models
  - Implementing authentication
  - Writing API tests
  - Setting up database migrations
---

# Backend Development Guidelines

> FastAPI + SQLAlchemy 2.0 + Pydantic v2 Development Standards

## Overview

This skill provides comprehensive guidelines for building robust, scalable FastAPI backends with modern Python practices.

### Tech Stack

| Layer      | Technology                    |
| ---------- | ----------------------------- |
| Framework  | FastAPI 0.110+                |
| ORM        | SQLAlchemy 2.0                |
| Validation | Pydantic v2                   |
| Database   | PostgreSQL                    |
| Migrations | Alembic                       |
| Testing    | pytest, pytest-asyncio, httpx |
| Auth       | JWT (python-jose)             |

## Core Principles

### 1. API-First Design

- Define schemas before implementation
- Use Pydantic models for request/response validation
- Document endpoints with docstrings
- Return consistent response structures

### 2. Repository Pattern

- Separate data access from business logic
- Use dependency injection for database sessions
- Abstract database operations behind interfaces

### 3. Test-Driven Development

- Write tests before implementation
- Use test database (SQLite in-memory or test Postgres)
- Mock external dependencies
- Target 80%+ coverage for API code

## Quick Reference

### File Structure

```
app/
├── api/
│   ├── deps.py          # Dependencies (db session, auth)
│   └── v1/
│       ├── endpoints/
│       │   └── users.py
│       └── router.py
├── core/
│   ├── config.py        # Settings management
│   └── security.py      # Password hashing, JWT
├── db/
│   ├── base.py          # Base model, session
│   └── migrations/      # Alembic migrations
├── models/
│   └── user.py          # SQLAlchemy models
├── schemas/
│   └── user.py          # Pydantic schemas
├── repositories/
│   └── user.py          # Repository classes
└── main.py              # App factory
```

### Dependencies

```python
# api/deps.py
from typing import Generator
from app.db.base import SessionLocal

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Router Pattern

```python
# api/v1/endpoints/users.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db

router = APIRouter()

@router.get("/users")
def list_users(db: Session = Depends(get_db)):
    return {"users": []}
```

## Code Generation

Use the endpoint generator:

```bash
python .agent/skills/backend-dev-guidelines/scripts/generate-endpoint.py User
```

Generates:

- Pydantic schemas (Create, Update, Response)
- SQLAlchemy model
- Repository class
- FastAPI router with CRUD
- pytest test file

## Response Format

Standard response envelope:

```json
{
  "data": {},
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100
  }
}
```

Error response format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": []
  }
}
```

## References

- [API Patterns](references/api-patterns.md) - RESTful design, error handling, pagination
- [Database Models](references/database-models.md) - SQLAlchemy patterns, relationships
