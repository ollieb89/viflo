#!/usr/bin/env python3
"""
Generate database schema files from field definitions.

Usage:
    python generate-schema.py User --fields "email:str,name:str,active:bool"
    python generate-schema.py Product --fields "name:str,price:float,category_id:int"

Generates:
- SQLAlchemy 2.0 model
- Alembic migration stub
- Pydantic schemas
- Repository class
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime


MODEL_TEMPLATE = '''"""
{table_name} model.
"""
from sqlalchemy import String, Boolean, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db.base import Base, TimestampMixin


class {class_name}(Base, TimestampMixin):
    """{class_name} database model."""
    
    __tablename__ = "{table_name}"
    
    id: Mapped[int] = mapped_column(primary_key=True)
{fields}
    
    # Relationships
    # Example: owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # Example: owner: Mapped["User"] = relationship(back_populates="{relationship_name}")
'''


MIGRATION_TEMPLATE = '''"""
{revision_id}

Create {table_name} table.

Revision ID: {revision_id}
Revises: 
Create Date: {create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '{revision_id}'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        '{table_name}',
        sa.Column('id', sa.Integer(), nullable=False),
{columns}
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes for foreign keys and commonly queried fields
{indexes}


def downgrade() -> None:
    op.drop_table('{table_name}')
'''


SCHEMA_TEMPLATE = '''"""
{table_name} schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class {class_name}Base(BaseModel):
    """Base {class_name} schema."""
{base_fields}


class {class_name}Create({class_name}Base):
    """Schema for creating a new {class_name}."""
    pass


class {class_name}Update(BaseModel):
    """Schema for updating a {class_name}."""
{update_fields}


class {class_name}InDB({class_name}Base):
    """Schema representing a {class_name} as stored in the database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


class {class_name}Response(BaseModel):
    """API response wrapper."""
    data: {class_name}InDB


class {class_name}ListResponse(BaseModel):
    """API response wrapper for list."""
    data: list[{class_name}InDB]
    meta: dict
'''


REPO_TEMPLATE = '''"""
{table_name} repository.
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.{module_name} import {class_name}
from app.schemas.{module_name} import {class_name}Create, {class_name}Update
from .base import BaseRepository


class {class_name}Repository(BaseRepository[{class_name}, {class_name}Create, {class_name}Update]):
    """Repository for {class_name} operations."""
    
    def get_by_{first_field}(self, db: Session, {first_field}: str) -> Optional[{class_name}]:
        """Get {class_name} by {first_field}."""
        stmt = select({class_name}).where({class_name}.{first_field} == {first_field})
        return db.execute(stmt).scalar_one_or_none()


# Singleton instance
{repo_name}_repo = {class_name}Repository({class_name})
'''


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


def parse_fields(fields_str: str | None) -> list[tuple[str, str]]:
    """Parse field definitions like 'name:str,price:float'."""
    if not fields_str:
        return [("name", "str")]
    
    fields = []
    for field_def in fields_str.split(","):
        parts = field_def.strip().split(":")
        name = parts[0].strip()
        type_ = parts[1].strip() if len(parts) > 1 else "str"
        fields.append((name, type_))
    return fields


def get_sqlalchemy_type(py_type: str) -> tuple[str, str]:
    """Convert Python type to SQLAlchemy column type."""
    type_map = {
        "str": ("String(255)", "str"),
        "Optional[str]": ("String(255)", "Optional[str]"),
        "int": ("Integer", "int"),
        "Optional[int]": ("Integer", "Optional[int]"),
        "float": ("Float", "float"),
        "Optional[float]": ("Float", "Optional[float]"),
        "bool": ("Boolean", "bool"),
        "Optional[bool]": ("Boolean", "Optional[bool]"),
        "datetime": ("DateTime(timezone=True)", "datetime"),
        "text": ("Text", "str"),
        "uuid": ("UUID(as_uuid=True)", "UUID"),
        "jsonb": ("JSONB", "dict"),
    }
    base_type = py_type.replace("Optional[", "").replace("]", "").lower()
    return type_map.get(base_type, ("String(255)", py_type))


def generate_model_fields(fields: list[tuple[str, str]]) -> str:
    """Generate SQLAlchemy model field definitions."""
    lines = []
    for name, py_type in fields:
        sa_type, mapped_type = get_sqlalchemy_type(py_type)
        if "Optional" in py_type or py_type.startswith("Optional"):
            lines.append(f"    {name}: Mapped[{mapped_type}] = mapped_column({sa_type}, nullable=True)")
        else:
            lines.append(f"    {name}: Mapped[{mapped_type}] = mapped_column({sa_type})")
    return "\n".join(lines)


def generate_migration_columns(fields: list[tuple[str, str]]) -> str:
    """Generate Alembic column definitions."""
    lines = []
    for name, py_type in fields:
        sa_type, _ = get_sqlalchemy_type(py_type)
        nullable = "Optional" in py_type
        lines.append(f"        sa.Column('{name}', sa.{sa_type}, nullable={str(nullable)}),")
    return "\n".join(lines)


def generate_migration_indexes(fields: list[tuple[str, str]], table_name: str) -> str:
    """Generate index definitions for foreign keys and common fields."""
    lines = []
    for name, _ in fields:
        if name.endswith('_id'):
            lines.append(f"    op.create_index(op.f('ix_{table_name}_{name}'), '{table_name}', ['{name}'], unique=False)")
        elif name in ['email', 'slug', 'name']:
            lines.append(f"    # Consider: op.create_index(op.f('ix_{table_name}_{name}'), '{table_name}', ['{name}'], unique=False)")
    return "\n".join(lines) if lines else "    # Add indexes as needed"


def generate_schema_fields(fields: list[tuple[str, str]]) -> tuple[str, str]:
    """Generate Pydantic schema fields."""
    base_lines = []
    update_lines = []
    for name, type_ in fields:
        base_lines.append(f"    {name}: {type_}")
        update_lines.append(f"    {name}: Optional[{type_}] = None")
    return "\n".join(base_lines), "\n".join(update_lines)


def generate_revision_id() -> str:
    """Generate Alembic-style revision ID."""
    import random
    chars = '0123456789abcdef'
    return ''.join(random.choice(chars) for _ in range(12))


def generate_schema(class_name: str, fields_str: str | None, output_dir: str):
    """Generate all schema files."""
    module_name = to_snake_case(class_name)
    table_name = to_plural(module_name)
    repo_name = module_name
    relationship_name = to_plural(module_name)
    
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    
    fields = parse_fields(fields_str)
    first_field = fields[0][0] if fields else "name"
    
    # Generate model
    models_dir = output / "models"
    models_dir.mkdir(exist_ok=True)
    model_content = MODEL_TEMPLATE.format(
        class_name=class_name,
        table_name=table_name,
        module_name=module_name,
        relationship_name=relationship_name,
        fields=generate_model_fields(fields),
    )
    (models_dir / f"{module_name}.py").write_text(model_content)
    print(f"✅ Created: models/{module_name}.py")
    
    # Generate migration
    migrations_dir = output / "alembic" / "versions"
    migrations_dir.mkdir(parents=True, exist_ok=True)
    revision_id = generate_revision_id()
    migration_content = MIGRATION_TEMPLATE.format(
        revision_id=revision_id,
        table_name=table_name,
        create_date=datetime.now().isoformat(),
        columns=generate_migration_columns(fields),
        indexes=generate_migration_indexes(fields, table_name),
    )
    (migrations_dir / f"{revision_id}_create_{table_name}.py").write_text(migration_content)
    print(f"✅ Created: alembic/versions/{revision_id}_create_{table_name}.py")
    
    # Generate schemas
    schemas_dir = output / "schemas"
    schemas_dir.mkdir(exist_ok=True)
    base_fields, update_fields = generate_schema_fields(fields)
    schema_content = SCHEMA_TEMPLATE.format(
        class_name=class_name,
        table_name=table_name,
        base_fields=base_fields,
        update_fields=update_fields,
    )
    (schemas_dir / f"{module_name}.py").write_text(schema_content)
    print(f"✅ Created: schemas/{module_name}.py")
    
    # Generate repository
    repos_dir = output / "repositories"
    repos_dir.mkdir(exist_ok=True)
    repo_content = REPO_TEMPLATE.format(
        class_name=class_name,
        table_name=table_name,
        module_name=module_name,
        repo_name=repo_name,
        first_field=first_field,
    )
    (repos_dir / f"{module_name}.py").write_text(repo_content)
    print(f"✅ Created: repositories/{module_name}.py")
    
    print(f"\n🎉 Generated schema for '{class_name}'!")
    print(f"\nNext steps:")
    print(f"  1. Review the generated files")
    print(f"  2. Add relationships if needed")
    print(f"  3. Run migration: alembic upgrade head")


def main():
    parser = argparse.ArgumentParser(
        description="Generate database schema files from field definitions"
    )
    parser.add_argument(
        "class_name",
        help="Model class name in PascalCase (e.g., User, Product, OrderItem)"
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
    
    # Validate class name
    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', args.class_name):
        print("Error: Class name must be PascalCase (e.g., 'User', 'Product')")
        sys.exit(1)
    
    generate_schema(args.class_name, args.fields, args.output)


if __name__ == "__main__":
    main()
