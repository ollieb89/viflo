# API Design Patterns

> RESTful API patterns for FastAPI

## RESTful Resource Naming

```
GET    /items           # List all items
GET    /items/{id}      # Get single item
POST   /items           # Create new item
PUT    /items/{id}      # Full update
PATCH  /items/{id}      # Partial update
DELETE /items/{id}      # Delete item
```

### Nested Resources

```
GET    /users/{id}/posts     # List user's posts
POST   /users/{id}/posts     # Create post for user
GET    /users/{id}/posts/{pid}
```

## CRUD Endpoint Patterns

### List Endpoint

```python
@router.get("/items", response_model=ItemsResponse)
def list_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List items with pagination."""
    items = item_repo.get_multi(db, skip=skip, limit=limit)
    total = item_repo.count(db)
    return {
        "data": items,
        "meta": {"skip": skip, "limit": limit, "total": total}
    }
```

### Create Endpoint

```python
@router.post("/items", response_model=ItemResponse, status_code=201)
def create_item(
    item_in: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new item."""
    item = item_repo.create(db, obj_in=item_in, owner_id=current_user.id)
    return {"data": item}
```

### Update Endpoint

```python
@router.patch("/items/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    item_in: ItemUpdate,
    db: Session = Depends(get_db)
):
    """Partial update of an item."""
    item = item_repo.get(db, id=item_id)
    if not item:
        raise HTTPException(404, detail="Item not found")
    item = item_repo.update(db, db_obj=item, obj_in=item_in)
    return {"data": item}
```

### Delete Endpoint

```python
@router.delete("/items/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """Delete an item."""
    item = item_repo.get(db, id=item_id)
    if not item:
        raise HTTPException(404, detail="Item not found")
    item_repo.remove(db, id=item_id)
    return None
```

## Pydantic Schemas

### Base Pattern

```python
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class ItemCreate(ItemBase):
    """Required fields for creation."""
    pass

class ItemUpdate(BaseModel):
    """All fields optional for partial update."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class ItemInDB(ItemBase):
    """Database representation."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

class ItemResponse(BaseModel):
    """API response wrapper."""
    data: ItemInDB
```

## Error Handling

### Custom Exception Handler

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": str(exc)
            }
        }
    )
```

### HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Successful GET, PUT, PATCH |
| 201 | Successful POST (created) |
| 204 | Successful DELETE (no content) |
| 400 | Bad request, validation error |
| 401 | Unauthorized (not authenticated) |
| 403 | Forbidden (no permission) |
| 404 | Resource not found |
| 409 | Conflict (duplicate, state conflict) |
| 422 | Validation error (Pydantic) |
| 500 | Internal server error |

## Pagination Strategies

### Offset Pagination

```python
from typing import Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    meta: dict

@router.get("/items", response_model=PaginatedResponse[ItemInDB])
def list_items(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * per_page
    items = repo.get_multi(db, skip=skip, limit=per_page)
    total = repo.count(db)
    
    return {
        "data": items,
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }
```

### Cursor Pagination (for large datasets)

```python
@router.get("/items")
def list_items_cursor(
    cursor: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    items = repo.get_page(db, cursor=cursor, limit=limit)
    next_cursor = encode_cursor(items[-1].id) if len(items) == limit else None
    
    return {
        "data": items,
        "meta": {
            "next_cursor": next_cursor,
            "limit": limit
        }
    }
```

## Authentication with JWT

### Login Endpoint

```python
from datetime import timedelta
from app.core.security import create_access_token, verify_password

@router.post("/login")
def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = user_repo.get_by_email(db, email=credentials.username)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(401, detail="Invalid credentials")
    
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(hours=24)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
```

### Protected Route

```python
from app.core.security import get_current_user

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user."""
    return {"data": current_user}
```

## Dependency Injection Patterns

### Database Session

```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Current User with Roles

```python
class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(403, detail="Insufficient permissions")
        return user

require_admin = RoleChecker(["admin"])

@router.delete("/users/{id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    ...
```

### Settings Injection

```python
from functools import lru_cache
from app.core.config import Settings

@lru_cache
def get_settings() -> Settings:
    return Settings()

@router.get("/config")
def get_config(settings: Settings = Depends(get_settings)):
    return {"debug": settings.DEBUG}
```
