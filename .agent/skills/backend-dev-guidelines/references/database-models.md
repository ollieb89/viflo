# Database Modeling Patterns

> SQLAlchemy 2.0 patterns for FastAPI

## Declarative Models

### Base Model

```python
# db/base.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    """Adds created_at and updated_at columns."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
```

### Basic Model

```python
# models/user.py
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    # Relationships
    items: Mapped[list["Item"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan"
    )
```

## Relationship Patterns

### One-to-Many

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    posts: Mapped[list["Post"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan"
    )

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="posts")
```

### Many-to-Many

```python
# Association table
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True)
)

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    tags: Mapped[list["Tag"]] = relationship(
        secondary=post_tags,
        back_populates="posts"
    )

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    posts: Mapped[list["Post"]] = relationship(
        secondary=post_tags,
        back_populates="tags"
    )
```

### Self-Referential

```python
class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"),
        nullable=True
    )

    parent: Mapped["Category"] = relationship(
        back_populates="children",
        remote_side=[id]
    )
    children: Mapped[list["Category"]] = relationship(
        back_populates="parent"
    )
```

## Repository Pattern

### Base Repository

```python
# repositories/base.py
from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.get(self.model, id)

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        return db.execute(stmt).scalars().all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        obj_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.get(self.model, id)
        db.delete(obj)
        db.commit()
        return obj

    def count(self, db: Session) -> int:
        stmt = select(func.count()).select_from(self.model)
        return db.execute(stmt).scalar()
```

### Concrete Repository

```python
# repositories/user.py
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from .base import BaseRepository

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return db.execute(stmt).scalar_one_or_none()

    def create_with_password(
        self,
        db: Session,
        *,
        obj_in: UserCreate,
        password: str
    ) -> User:
        from app.core.security import get_password_hash

        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(password),
            full_name=obj_in.full_name
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

user_repo = UserRepository(User)
```

## Unit of Work Pattern

```python
from contextlib import contextmanager
from typing import Generator

class UnitOfWork:
    def __init__(self, db: Session):
        self.db = db

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()

@contextmanager
def unit_of_work(db: Session) -> Generator[UnitOfWork, None, None]:
    uow = UnitOfWork(db)
    try:
        yield uow
        uow.commit()
    except Exception:
        uow.rollback()
        raise
```

## Migration Best Practices (Alembic)

### Initial Setup

```bash
alembic init alembic
```

### Configuration

```python
# alembic/env.py
from app.db.base import Base
from app.core.config import settings

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
target_metadata = Base.metadata
```

### Creating Migrations

```bash
# Auto-generate from models
alembic revision --autogenerate -m "add user table"

# Create empty migration
alembic revision -m "add indexes"
```

### Migration Best Practices

```python
# Always make migrations reversible
def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

def downgrade():
    op.drop_table('users')
```

### Data Migrations

```python
def upgrade():
    # Add nullable column first
    op.add_column('users', sa.Column('status', sa.String(), nullable=True))

    # Migrate existing data
    op.execute("UPDATE users SET status = 'active'")

    # Make column non-nullable
    op.alter_column('users', 'status', nullable=False)
```

## Soft Delete Implementation

```python
from sqlalchemy import event
from datetime import datetime

class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

# Override repository methods
class SoftDeleteRepository(BaseRepository):
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        stmt = (
            select(self.model)
            .where(self.model.id == id)
            .where(self.model.deleted_at.is_(None))
        )
        return db.execute(stmt).scalar_one_or_none()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[ModelType]:
        stmt = select(self.model)
        if not include_deleted:
            stmt = stmt.where(self.model.deleted_at.is_(None))
        stmt = stmt.offset(skip).limit(limit)
        return db.execute(stmt).scalars().all()

    def remove(self, db: Session, *, id: int) -> ModelType:
        """Soft delete instead of hard delete."""
        obj = db.get(self.model, id)
        obj.deleted_at = datetime.utcnow()
        db.commit()
        db.refresh(obj)
        return obj

    def restore(self, db: Session, *, id: int) -> ModelType:
        """Restore soft-deleted item."""
        obj = db.get(self.model, id)
        obj.deleted_at = None
        db.commit()
        db.refresh(obj)
        return obj

    def hard_delete(self, db: Session, *, id: int) -> ModelType:
        """Permanently delete."""
        return super().remove(db, id=id)
```

## Query Patterns

### Filtering

```python
from sqlalchemy import and_, or_

def filter_items(
    db: Session,
    name: str | None = None,
    min_price: float | None = None,
    is_active: bool | None = None
):
    stmt = select(Item)

    if name:
        stmt = stmt.where(Item.name.ilike(f"%{name}%"))
    if min_price:
        stmt = stmt.where(Item.price >= min_price)
    if is_active is not None:
        stmt = stmt.where(Item.is_active == is_active)

    return db.execute(stmt).scalars().all()
```

### Eager Loading

```python
from sqlalchemy.orm import joinedload, selectinload

# Load user with items (one-to-many)
stmt = select(User).options(selectinload(User.items))
user = db.execute(stmt).scalar_one()

# Load item with owner (many-to-one)
stmt = select(Item).options(joinedload(Item.owner))
items = db.execute(stmt).scalars().all()

# Load posts with tags (many-to-many)
stmt = select(Post).options(selectinload(Post.tags))
posts = db.execute(stmt).scalars().all()
```

### Aggregation

```python
from sqlalchemy import func

# Count items per user
stmt = (
    select(User.id, User.email, func.count(Item.id).label("item_count"))
    .join(Item, User.id == Item.user_id)
    .group_by(User.id)
)
results = db.execute(stmt).all()
```
