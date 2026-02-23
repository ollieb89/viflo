#!/usr/bin/env python3
"""
Generate FastAPI CRUD endpoint scaffolding.

Usage:
    python generate-endpoint.py User
    python generate-endpoint.py Product --fields name:str,price:float,active:bool
"""

import argparse
import re
import sys
from pathlib import Path


def generate_schema(resource_name: str, resource: str, fields: list[tuple[str, str]]) -> str:
    """Generate Pydantic schema file."""
    base_fields = "\n".join(f"    {name}: {type_}" for name, type_ in fields)
    update_fields = "\n".join(f"    {name}: Optional[{type_}] = None" for name, type_ in fields)
    
    return f'''"""
{resource_name} schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class {resource_name}Base(BaseModel):
    """Base {resource} schema with common attributes."""
{base_fields}


class {resource_name}Create({resource_name}Base):
    """Schema for creating a new {resource}."""
    pass


class {resource_name}Update(BaseModel):
    """Schema for updating a {resource} (all fields optional)."""
{update_fields}


class {resource_name}InDB({resource_name}Base):
    """Schema representing a {resource} as stored in the database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


class {resource_name}Response(BaseModel):
    """API response wrapper for single {resource}."""
    data: {resource_name}InDB


class {resource_name}ListResponse(BaseModel):
    """API response wrapper for {resource} list."""
    data: list[{resource_name}InDB]
    meta: dict
'''


def generate_model(resource_name: str, resource: str, resource_plural: str, fields: list[tuple[str, str]]) -> str:
    """Generate SQLAlchemy model file."""
    type_map = {
        "str": "String(255)",
        "Optional[str]": "String(255)",
        "int": "Integer",
        "float": "Float",
        "bool": "Boolean",
        "datetime": "DateTime(timezone=True)",
    }
    
    model_fields = []
    for name, py_type in fields:
        sa_type = type_map.get(py_type.replace("Optional[", "").replace("]", ""), "String(255)")
        if "Optional" in py_type:
            model_fields.append(f"    {name}: Mapped[{py_type}] = mapped_column({sa_type}, nullable=True)")
        else:
            model_fields.append(f"    {name}: Mapped[{py_type}] = mapped_column({sa_type})")
    
    fields_str = "\n".join(model_fields)
    
    return f'''"""
{resource_name} model.
"""
from sqlalchemy import String, Boolean, Float, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class {resource_name}(Base, TimestampMixin):
    """{resource_name} database model."""
    
    __tablename__ = "{resource_plural}"
    
    id: Mapped[int] = mapped_column(primary_key=True)
{fields_str}
    
    # Add relationships here
    # owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # owner: Mapped["User"] = relationship(back_populates="{resource_plural}")
'''


def generate_repository(resource_name: str, resource: str) -> str:
    """Generate repository file."""
    return f'''"""
{resource_name} repository.
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.{resource} import {resource_name}
from app.schemas.{resource} import {resource_name}Create, {resource_name}Update
from .base import BaseRepository


class {resource_name}Repository(BaseRepository[{resource_name}, {resource_name}Create, {resource_name}Update]):
    """Repository for {resource_name} operations."""
    
    def get_by_name(self, db: Session, name: str) -> Optional[{resource_name}]:
        """Get {resource} by name."""
        stmt = select({resource_name}).where({resource_name}.name == name)
        return db.execute(stmt).scalar_one_or_none()
    
    # Add custom repository methods here


# Singleton instance
{resource}_repo = {resource_name}Repository({resource_name})
'''


def generate_router(resource_name: str, resource: str, resource_plural: str) -> str:
    """Generate FastAPI router file."""
    return f'''"""
{resource_name} API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.{resource} import (
    {resource_name}Create,
    {resource_name}Update,
    {resource_name}Response,
    {resource_name}ListResponse,
)
from app.repositories.{resource} import {resource}_repo

router = APIRouter()


@router.get("/{resource_plural}", response_model={resource_name}ListResponse)
def list_{resource_plural}(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Retrieve {resource_plural} with pagination.
    """
    items = {resource}_repo.get_multi(db, skip=skip, limit=limit)
    total = {resource}_repo.count(db)
    return {{
        "data": items,
        "meta": {{
            "skip": skip,
            "limit": limit,
            "total": total,
        }},
    }}


@router.post("/{resource_plural}", response_model={resource_name}Response, status_code=status.HTTP_201_CREATED)
def create_{resource}(
    *,
    item_in: {resource_name}Create,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create new {resource}.
    """
    item = {resource}_repo.create(db, obj_in=item_in)
    return {{"data": item}}


@router.get("/{resource_plural}/{{{resource}_id}}", response_model={resource_name}Response)
def get_{resource}(
    *,
    {resource}_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a specific {resource} by ID.
    """
    item = {resource}_repo.get(db, id={resource}_id)
    if not item:
        raise HTTPException(status_code=404, detail="{resource_name} not found")
    return {{"data": item}}


@router.patch("/{resource_plural}/{{{resource}_id}}", response_model={resource_name}Response)
def update_{resource}(
    *,
    {resource}_id: int,
    item_in: {resource_name}Update,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a {resource}.
    """
    item = {resource}_repo.get(db, id={resource}_id)
    if not item:
        raise HTTPException(status_code=404, detail="{resource_name} not found")
    item = {resource}_repo.update(db, db_obj=item, obj_in=item_in)
    return {{"data": item}}


@router.delete("/{resource_plural}/{{{resource}_id}}", status_code=status.HTTP_204_NO_CONTENT)
def delete_{resource}(
    *,
    {resource}_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a {resource}.
    """
    item = {resource}_repo.get(db, id={resource}_id)
    if not item:
        raise HTTPException(status_code=404, detail="{resource_name} not found")
    {resource}_repo.remove(db, id={resource}_id)
    return None
'''


def generate_tests(resource_name: str, resource: str, resource_plural: str, fields: list[tuple[str, str]]) -> str:
    """Generate test file."""
    # Build test data dict
    test_data_pairs = []
    for name, py_type in fields:
        if "Optional" not in py_type:
            if "str" in py_type:
                test_data_pairs.append(f'"{name}": "Test Item"')
            elif "int" in py_type:
                test_data_pairs.append(f'"{name}": 1')
            elif "float" in py_type:
                test_data_pairs.append(f'"{name}": 10.99')
            elif "bool" in py_type:
                test_data_pairs.append(f'"{name}": True')
    test_data = ", ".join(test_data_pairs)
    
    return f'''"""
Tests for {resource} endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.{resource} import {resource_name}
from app.repositories.{resource} import {resource}_repo


class Test{resource_name}Endpoints:
    """Test suite for {resource} API endpoints."""
    
    def test_create_{resource}(
        self,
        client: TestClient,
        db: Session,
        auth_headers: dict,
    ):
        """Test creating a new {resource}."""
        data = {{{test_data}}}
        response = client.post(
            "/api/v1/{resource_plural}",
            json=data,
            headers=auth_headers,
        )
        assert response.status_code == 201
        content = response.json()
        assert content["data"]["name"] == data["name"]
    
    def test_get_{resource}(
        self,
        client: TestClient,
        db: Session,
    ):
        """Test getting a {resource} by ID."""
        # Create test {resource}
        item_data = {{{test_data}}}
        item = {resource}_repo.create(db, obj_in=item_data)
        
        response = client.get(f"/api/v1/{resource_plural}/{{item.id}}")
        assert response.status_code == 200
        content = response.json()
        assert content["data"]["id"] == item.id
    
    def test_get_{resource}_not_found(self, client: TestClient):
        """Test getting a non-existent {resource}."""
        response = client.get("/api/v1/{resource_plural}/99999")
        assert response.status_code == 404
    
    def test_list_{resource_plural}(
        self,
        client: TestClient,
        db: Session,
    ):
        """Test listing {resource_plural}."""
        # Create test {resource_plural}
        for i in range(3):
            {resource}_repo.create(db, obj_in=dict(name=f"Item {{i}}"))
        
        response = client.get("/api/v1/{resource_plural}")
        assert response.status_code == 200
        content = response.json()
        assert len(content["data"]) == 3
        assert "meta" in content
    
    def test_update_{resource}(
        self,
        client: TestClient,
        db: Session,
        auth_headers: dict,
    ):
        """Test updating a {resource}."""
        item_data = {{{test_data}}}
        item = {resource}_repo.create(db, obj_in=item_data)
        
        update_data = {{"name": "Updated Name"}}
        response = client.patch(
            f"/api/v1/{resource_plural}/{{item.id}}",
            json=update_data,
            headers=auth_headers,
        )
        assert response.status_code == 200
        content = response.json()
        assert content["data"]["name"] == "Updated Name"
    
    def test_delete_{resource}(
        self,
        client: TestClient,
        db: Session,
        auth_headers: dict,
    ):
        """Test deleting a {resource}."""
        item_data = {{{test_data}}}
        item = {resource}_repo.create(db, obj_in=item_data)
        
        response = client.delete(
            f"/api/v1/{resource_plural}/{{item.id}}",
            headers=auth_headers,
        )
        assert response.status_code == 204
        
        # Verify deletion
        response = client.get(f"/api/v1/{resource_plural}/{{item.id}}")
        assert response.status_code == 404
'''


def parse_fields(fields_str: str | None) -> list[tuple[str, str]]:
    """Parse field definitions like 'name:str,price:float,active:bool'."""
    if not fields_str:
        return [("name", "str"), ("description", "Optional[str]")]
    
    fields = []
    for field_def in fields_str.split(","):
        parts = field_def.strip().split(":")
        name = parts[0].strip()
        type_ = parts[1].strip() if len(parts) > 1 else "str"
        fields.append((name, type_))
    return fields


def to_snake_case(name: str) -> str:
    """Convert PascalCase to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def to_plural(name: str) -> str:
    """Simple pluralization."""
    if name.endswith('y'):
        return name[:-1] + 'ies'
    elif name.endswith(('s', 'x', 'z', 'ch', 'sh')):
        return name + 'es'
    return name + 's'


def generate_resource(resource_name: str, fields_str: str | None, output_dir: str):
    """Generate all files for a resource."""
    resource = to_snake_case(resource_name)
    resource_plural = to_plural(resource)
    table_name = resource_plural
    
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    
    fields = parse_fields(fields_str)
    
    # Generate schema
    schemas_dir = output / "schemas"
    schemas_dir.mkdir(exist_ok=True)
    schema_content = generate_schema(resource_name, resource, fields)
    (schemas_dir / f"{resource}.py").write_text(schema_content)
    print(f"✅ Created: schemas/{resource}.py")
    
    # Generate model
    models_dir = output / "models"
    models_dir.mkdir(exist_ok=True)
    model_content = generate_model(resource_name, resource, table_name, fields)
    (models_dir / f"{resource}.py").write_text(model_content)
    print(f"✅ Created: models/{resource}.py")
    
    # Generate repository
    repos_dir = output / "repositories"
    repos_dir.mkdir(exist_ok=True)
    repo_content = generate_repository(resource_name, resource)
    (repos_dir / f"{resource}.py").write_text(repo_content)
    print(f"✅ Created: repositories/{resource}.py")
    
    # Generate router
    endpoints_dir = output / "api" / "v1" / "endpoints"
    endpoints_dir.mkdir(parents=True, exist_ok=True)
    router_content = generate_router(resource_name, resource, resource_plural)
    (endpoints_dir / f"{resource}.py").write_text(router_content)
    print(f"✅ Created: api/v1/endpoints/{resource}.py")
    
    # Generate tests
    tests_dir = output / "tests" / "api"
    tests_dir.mkdir(parents=True, exist_ok=True)
    test_content = generate_tests(resource_name, resource, resource_plural, fields)
    (tests_dir / f"test_{resource}.py").write_text(test_content)
    print(f"✅ Created: tests/api/test_{resource}.py")
    
    print(f"\n🎉 Generated CRUD for '{resource_name}'!")
    print(f"\nNext steps:")
    print(f"  1. Add router to api/v1/router.py:")
    print(f"     from app.api.v1.endpoints.{resource} import router as {resource}_router")
    print(f"     router.include_router({resource}_router, prefix='/{resource_plural}', tags=['{resource_plural}'])")
    print(f"  2. Import model in db/base.py: from app.models.{resource} import {resource_name}")
    print(f"  3. Run migrations: alembic revision --autogenerate -m 'add {resource} table'")


def main():
    parser = argparse.ArgumentParser(
        description="Generate FastAPI CRUD endpoint scaffolding"
    )
    parser.add_argument(
        "resource",
        help="Resource name in PascalCase (e.g., User, Product, OrderItem)"
    )
    parser.add_argument(
        "--fields",
        help="Field definitions (e.g., 'name:str,price:float,active:bool')"
    )
    parser.add_argument(
        "--output",
        default=".",
        help="Output directory (default: current directory)"
    )
    
    args = parser.parse_args()
    
    # Validate resource name
    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', args.resource):
        print("Error: Resource name must be PascalCase (e.g., 'User', 'Product')")
        sys.exit(1)
    
    generate_resource(args.resource, args.fields, args.output)


if __name__ == "__main__":
    main()
