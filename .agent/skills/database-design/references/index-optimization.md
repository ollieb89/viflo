# Index Optimization Guide

> Strategies for optimal database indexing with PostgreSQL

## When to Add Indexes

### ✅ Add Indexes For

- **Foreign keys** - Always index foreign key columns
- **Frequently queried columns** - WHERE, JOIN, ORDER BY clauses
- **Unique constraints** - Enforce uniqueness efficiently
- **Text search** - Full-text search with GIN indexes

### ❌ Avoid Indexes On

- Small tables (< 1000 rows)
- Frequently updated columns
- Columns with low cardinality (boolean, status with few values)
- Columns rarely used in queries

---

## Index Types

### B-Tree (Default)

```python
Index('ix_users_email', 'email')  # Equality and range queries
```

**Best for:**

- Equality: `WHERE email = 'user@example.com'`
- Range: `WHERE created_at > '2024-01-01'`
- Ordering: `ORDER BY created_at`

### GIN (Generalized Inverted Index)

```python
from sqlalchemy.dialects.postgresql import JSONB

class Event(Base):
    payload: Mapped[dict] = mapped_column(JSONB)

    __table_args__ = (
        Index('ix_events_payload', 'payload', postgresql_using='gin'),
    )
```

**Best for:**

- JSONB columns
- Array columns
- Full-text search

### GiST (Generalized Search Tree)

```python
# For geometric data, ranges
from sqlalchemy.dialects.postgresql import TSTZRANGE

class Reservation(Base):
    period: Mapped[TSTZRANGE]

    __table_args__ = (
        Index('ix_reservations_period', 'period', postgresql_using='gist'),
    )
```

---

## Composite Indexes

### Column Ordering

```python
# Good: High selectivity first
Index('ix_users_org_email', 'organization_id', 'email')

# Query pattern:
# WHERE organization_id = 1 AND email = 'user@example.com'
```

**Rules:**

1. Equality columns first (=)
2. Range columns second (>, <, BETWEEN)
3. Low cardinality columns last

### Covering Indexes

```python
# Index-only scan possible
Index('ix_users_email_name', 'email', 'name', 'created_at')

# Query can use index-only scan:
# SELECT name, created_at FROM users WHERE email = 'x'
```

---

## Partial Indexes

```python
# Only index active users
Index('ix_active_users_email', 'email',
      postgresql_where="is_active = true")

# Query:
# SELECT * FROM users WHERE is_active = true AND email = 'x'
```

**Benefits:**

- Smaller index size
- Faster queries on subset
- Efficient for soft deletes

---

## Expression Indexes

```python
# Case-insensitive lookup
Index('ix_users_email_lower', func.lower(User.email))

# Query:
# SELECT * FROM users WHERE lower(email) = lower('User@Example.com')
```

---

## Migration Best Practices

### Creating Indexes Concurrently

```python
# Migration file
from alembic import op

def upgrade():
    # For large tables, use concurrent index creation
    op.create_index(
        'ix_large_table_column',
        'large_table',
        ['column'],
        postgresql_concurrently=True
    )
```

**Note:** `CONCURRENTLY` cannot run inside a transaction.

### Adding Indexes to Existing Tables

```python
# Step 1: Add index concurrently (no lock)
op.create_index(
    'ix_users_new_column',
    'users',
    ['new_column'],
    postgresql_concurrently=True
)

# Step 2: Analyze table
op.execute("ANALYZE users")
```

---

## Analyzing Index Usage

### Check Index Usage

```sql
-- PostgreSQL index usage statistics
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,        -- Number of index scans
    idx_tup_read,    -- Tuples read via index
    idx_tup_fetch    -- Tuples fetched via index
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

### Find Missing Indexes

```sql
-- Tables with sequential scans
SELECT
    schemaname,
    tablename,
    seq_scan,        -- Sequential scans
    seq_tup_read,    -- Tuples read sequentially
    idx_scan,        -- Index scans
    n_live_tup       -- Estimated live tuples
FROM pg_stat_user_tables
WHERE schemaname = 'public'
  AND seq_scan > 100
  AND (idx_scan IS NULL OR seq_scan > idx_scan * 10)
ORDER BY seq_tup_read DESC;
```

### Unused Indexes

```sql
-- Indexes rarely used (consider dropping)
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan < 10
  AND indexrelname NOT LIKE '%pkey%'
ORDER BY idx_scan;
```

---

## Common Mistakes

### 1. Too Many Indexes

```python
# Bad: Index every column
Index('ix_users_email', 'email')
Index('ix_users_name', 'name')
Index('ix_users_phone', 'phone')
Index('ix_users_status', 'status')  # Low cardinality!

# Better: Composite index for common queries
Index('ix_users_email_status', 'email', 'status')
```

### 2. Wrong Column Order

```python
# Bad: Range column first
Index('ix_orders_date_status', 'created_at', 'status')

# Better: Equality first, then range
Index('ix_orders_status_date', 'status', 'created_at')
```

### 3. Ignoring Write Performance

Each index:

- Speeds up SELECTs
- Slows down INSERT/UPDATE/DELETE
- Uses disk space

**Rule of thumb:** 3-5 indexes per table maximum.

---

## Performance Checklist

Before adding an index:

- [ ] Query runs slowly (>100ms)?
- [ ] EXPLAIN shows Seq Scan?
- [ ] Column has good selectivity?
- [ ] Table is large (>10K rows)?
- [ ] Index supports actual query patterns?

After adding an index:

- [ ] Query uses Index Scan?
- [ ] Execution time improved?
- [ ] Write performance acceptable?
- [ ] Index size reasonable?

---

## Quick Reference

| Scenario           | Index Type     | Example                               |
| ------------------ | -------------- | ------------------------------------- |
| Primary key lookup | B-Tree         | `WHERE id = 1`                        |
| Foreign key        | B-Tree         | `JOIN ON user_id`                     |
| Text search        | GIN            | `WHERE payload @> '{"key": "value"}'` |
| Array contains     | GIN            | `WHERE tags && ['python']`            |
| Range queries      | B-Tree         | `WHERE created_at > '2024-01-01'`     |
| Partial data       | Partial B-Tree | `WHERE is_active = true`              |
| Case-insensitive   | Expression     | `WHERE lower(email) = 'x'`            |
