---
name: database-design
description: |
  Database design principles and PostgreSQL patterns. Schema generation, 
  migration management, indexing strategies, and performance optimization. 
  Use when designing schemas, creating migrations, or optimizing queries.
triggers:
  - Designing database schema
  - Creating SQLAlchemy models
  - Writing Alembic migrations
  - Optimizing queries
  - Choosing indexes
  - Setting up PostgreSQL
---

# Database Design

> **PostgreSQL + SQLAlchemy 2.0 database design patterns**

## Quick Start

### Generate Schema

```bash
python .agent/skills/database-design/scripts/generate-schema.py User \
    --fields "email:str,name:str,active:bool"
```

Generates:

- SQLAlchemy 2.0 model
- Alembic migration
- Pydantic schemas
- Repository class

### Check Migration Safety

```bash
python .agent/skills/database-design/scripts/migration-helper.py safety \
    alembic/versions/xxx.py
```

### Start PostgreSQL

```bash
cd .agent/skills/database-design/assets/templates/postgres-setup
docker-compose up -d
```

---

## Schema Design Checklist

Before creating tables:

- [ ] Chosen appropriate data types
- [ ] Defined primary keys (UUID vs sequential)
- [ ] Planned foreign key relationships
- [ ] Considered index strategy
- [ ] Added created_at/updated_at timestamps
- [ ] Planned for soft deletes if needed

---

## Code Generation

### Schema Generator

```bash
# Basic usage
python generate-schema.py Product --fields "name:str,price:float"

# With all field types
python generate-schema.py Order \
    --fields "customer_id:int,total:float,status:str,metadata:jsonb"
```

**Supported types:** `str`, `int`, `float`, `bool`, `datetime`, `text`, `uuid`, `jsonb`

### Migration Helper

```bash
# Check all migrations
python migration-helper.py check

# Check specific migration
python migration-helper.py check alembic/versions/xxx.py

# Show migration status
python migration-helper.py status

# Check production safety
python migration-helper.py safety alembic/versions/xxx.py
```

---

## PostgreSQL Patterns

### Data Types

| Type        | Use When                         | SQLAlchemy                |
| ----------- | -------------------------------- | ------------------------- |
| UUID        | Distributed systems, exposed IDs | `UUID(as_uuid=True)`      |
| JSONB       | Flexible schema, nested data     | `JSONB`                   |
| ARRAY       | Lists of values                  | `ARRAY(String)`           |
| ENUM        | Fixed set of values              | `Enum(Status)`            |
| TIMESTAMPTZ | Date/time with timezone          | `DateTime(timezone=True)` |

### Essential Indexes

```python
# Foreign keys (always index)
user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

# Unique constraints
email: Mapped[str] = mapped_column(unique=True)

# Composite for common queries
__table_args__ = (
    Index('ix_orders_user_date', 'user_id', 'created_at'),
)
```

---

## Migration Best Practices

### Safe Migrations

1. **Add column**: `nullable=True` first, backfill, then `nullable=False`
2. **Add index**: Use `postgresql_concurrently=True` for large tables
3. **Drop column**: Check no queries use it first
4. **Rename**: Add new column, migrate data, drop old column

### Migration Safety Check

Always run before production:

```bash
python migration-helper.py safety alembic/versions/xxx.py
```

**Flags unsafe operations:**

- DROP TABLE / COLUMN
- ALTER COLUMN TYPE (rewrites table)
- ADD COLUMN NOT NULL without default

---

## Performance

### Query Optimization

```python
# Use selectinload for relationships
from sqlalchemy.orm import selectinload

stmt = select(User).options(selectinload(User.orders))
```

### Index Strategy

- **B-Tree**: Default, good for equality and range
- **GIN**: JSONB, arrays, full-text search
- **Partial**: Index subset of data (e.g., active users)
- **Expression**: Lowercase emails, computed values

---

## References

| File                                                        | Description                  |
| ----------------------------------------------------------- | ---------------------------- |
| [postgresql-patterns.md](references/postgresql-patterns.md) | UUID, JSONB, arrays, RLS     |
| [index-optimization.md](references/index-optimization.md)   | Index types, optimization    |
| [schema-design.md](schema-design.md)                        | Normalization, relationships |
| [migrations.md](migrations.md)                              | Migration patterns           |

---

## Templates

| Template          | Purpose                            |
| ----------------- | ---------------------------------- |
| `postgres-setup/` | Docker Compose + PostgreSQL config |

---

## Anti-Patterns

❌ **Default to PostgreSQL** for simple apps (SQLite may suffice)  
❌ **Skip indexing** on foreign keys and query columns  
❌ **Use SELECT \*** - specify columns explicitly  
❌ **Store JSON** when structured data is better  
❌ **Ignore N+1 queries** - use eager loading  
❌ **Big migrations** without testing on production-like data

---

## Decision Framework

### Choosing Database

| Use Case                  | Recommendation       |
| ------------------------- | -------------------- |
| Simple app, single user   | SQLite               |
| Web app, moderate traffic | PostgreSQL           |
| Serverless/edge           | Neon, Supabase       |
| Multi-region              | CockroachDB, Spanner |

### When to Index

- Foreign keys: **Always**
- Frequently queried columns: **Yes**
- Low cardinality (< 100 distinct): **No**
- Small tables (< 1000 rows): **No**
