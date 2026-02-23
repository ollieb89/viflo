# PostgreSQL Patterns

> Advanced PostgreSQL patterns for application development

## Table of Contents

1. [Data Types](#data-types)
2. [Constraints & Indexes](#constraints--indexes)
3. [Full-Text Search](#full-text-search)
4. [Triggers & Functions](#triggers--functions)
5. [Partitioning](#partitioning)
6. [Row Level Security](#row-level-security)

---

## Data Types

### UUID Primary Keys

```python
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
```

**When to use:**

- Distributed systems
- Exposing IDs in URLs (not sequential)
- Merging data from multiple sources

### JSONB for Flexible Data

```python
from sqlalchemy.dialects.postgresql import JSONB

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str]
    payload: Mapped[dict] = mapped_column(JSONB, default={})

    # Index for JSONB queries
    __table_args__ = (
        Index('ix_events_payload', 'payload', postgresql_using='gin'),
    )
```

**Querying JSONB:**

```python
# Find events with specific payload
stmt = select(Event).where(Event.payload["user_id"].as_integer() == 123)

# Check if key exists
stmt = select(Event).where(Event.payload.has_key("error"))
```

### Arrays

```python
from sqlalchemy.dialects.postgresql import ARRAY

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
```

### Enumerations

```python
import enum
from sqlalchemy import Enum as SQLEnum

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class User(Base):
    __tablename__ = "users"

    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus),
        default=UserStatus.ACTIVE
    )
```

---

## Constraints & Indexes

### Unique Constraints

```python
from sqlalchemy import UniqueConstraint

class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        UniqueConstraint('email', 'organization_id', name='uix_user_org_email'),
    )
```

### Partial Indexes

```python
class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        # Only index active users
        Index('ix_users_email_active', 'email',
              postgresql_where="is_active = true"),
    )
```

### Expression Indexes

```python
class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        # Case-insensitive email lookup
        Index('ix_users_email_lower', func.lower(email)),
    )
```

---

## Full-Text Search

```python
class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    content: Mapped[str]

    __table_args__ = (
        Index('ix_articles_search',
              text("to_tsvector('english', title || ' ' || content)"),
              postgresql_using='gin'),
    )
```

---

## Row Level Security

```sql
-- Enable RLS on table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY document_access_policy ON documents
    FOR ALL
    TO application_user
    USING (owner_id = current_setting('app.current_user_id')::int);
```

---

## Best Practices

1. **Index Strategy**: Index foreign keys, use partial indexes for filtered queries
2. **Constraints**: Use check constraints, deferrable constraints for transactions
3. **Performance**: Partition large tables, use connection pooling
4. **Migration Safety**: Create indexes CONCURRENTLY, validate constraints separately
