#!/usr/bin/env python3
"""
Migration helper for Alembic migrations.

Usage:
    python migration-helper.py check <migration_file>  # Check for issues
    python migration-helper.py status                  # Show migration status
    python migration-helper.py safety <migration_file> # Check safety

Commands:
    check   - Validate migration syntax and best practices
    status  - Show current migration status
    safety  - Check for destructive operations
    history - Show migration history
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime


def find_migrations(migrations_dir: Path) -> list[Path]:
    """Find all migration files."""
    if not migrations_dir.exists():
        return []
    return sorted(migrations_dir.glob("*.py"))


def check_migration(file_path: Path) -> list[str]:
    """Check migration for common issues."""
    issues = []
    
    try:
        content = file_path.read_text()
        
        # Check for common issues
        if "drop_table" in content and "batch_alter_table" not in content:
            issues.append("⚠️  Contains drop_table - ensure data is backed up")
        
        if "drop_column" in content:
            issues.append("⚠️  Contains drop_column - data will be lost")
        
        # Check for index creation without concurrent
        if "create_index" in content and "postgresql_concurrently" not in content:
            issues.append("💡 Consider using postgresql_concurrently=True for large tables")
        
        # Check for nullable changes on existing columns
        if re.search(r"alter_column.*nullable", content):
            issues.append("⚠️  Changing nullable constraint - check for NULL values")
        
        # Check for type changes
        if re.search(r"alter_column.*type_", content):
            issues.append("⚠️  Changing column type - may cause data loss")
        
        # Check for missing downgrades
        if "def downgrade():" in content:
            downgrade_content = content.split("def downgrade():")[1]
            if not downgrade_content.strip() or downgrade_content.strip() == "pass":
                issues.append("⚠️  Empty downgrade function")
        
        # Check for proper imports
        if "from alembic import op" not in content:
            issues.append("❌ Missing 'from alembic import op'")
        
        # Good practices
        if "\"\"\"" not in content:
            issues.append("💡 Add docstring describing migration purpose")
            
    except Exception as e:
        issues.append(f"❌ Error reading file: {e}")
    
    return issues


def check_safety(file_path: Path) -> dict:
    """Check migration safety for production."""
    result = {
        "safe": True,
        "warnings": [],
        "blocking_operations": [],
        "recommendations": []
    }
    
    try:
        content = file_path.read_text()
        
        # Destructive operations
        destructive_patterns = [
            (r"op\\.drop_table", "DROP TABLE - Data will be lost"),
            (r"op\\.drop_column", "DROP COLUMN - Data will be lost"),
            (r"op\\.execute.*DELETE", "DELETE without WHERE - Mass deletion"),
            (r"op\\.execute.*TRUNCATE", "TRUNCATE - All data removed"),
        ]
        
        for pattern, description in destructive_patterns:
            if re.search(pattern, content):
                result["blocking_operations"].append(description)
                result["safe"] = False
        
        # Blocking operations (table locks)
        blocking_patterns = [
            (r"create_index.*\\)", "CREATE INDEX - Locks table"),
            (r"add_column.*nullable=False", "ADD COLUMN NOT NULL - Table rewrite"),
            (r"alter_column.*type_", "ALTER COLUMN TYPE - Table rewrite"),
        ]
        
        for pattern, description in blocking_patterns:
            if re.search(pattern, content):
                result["warnings"].append(description)
        
        # Recommendations
        if "create_index" in content and "postgresql_concurrently" not in content:
            result["recommendations"].append(
                "Use postgresql_concurrently=True for index creation on large tables"
            )
        
        if "add_column" in content and "server_default" not in content:
            result["recommendations"].append(
                "Consider adding server_default for new non-nullable columns"
            )
            
    except Exception as e:
        result["warnings"].append(f"Error analyzing file: {e}")
    
    return result


def show_status(migrations_dir: Path):
    """Show migration status."""
    migrations = find_migrations(migrations_dir)
    
    print(f"\n📊 Migration Status")
    print("=" * 60)
    print(f"Migrations directory: {migrations_dir}")
    print(f"Total migrations: {len(migrations)}")
    print()
    
    if not migrations:
        print("No migrations found.")
        return
    
    print("Recent migrations:")
    print("-" * 60)
    
    for migration in migrations[-10:]:  # Show last 10
        # Extract revision and description
        content = migration.read_text()
        
        # Try to extract docstring
        docstring_match = re.search(r'\"\"\"(.+?)\"\"\"', content, re.DOTALL)
        if docstring_match:
            lines = docstring_match.group(1).strip().split('\n')
            description = lines[0][:50] if lines else "No description"
        else:
            description = "No description"
        
        print(f"  {migration.name:<50} {description}")
    
    print()


def show_history(migrations_dir: Path, count: int = 20):
    """Show migration history with dependencies."""
    migrations = find_migrations(migrations_dir)
    
    print(f"\n📜 Migration History (last {count})")
    print("=" * 60)
    
    for migration in migrations[-count:]:
        content = migration.read_text()
        
        # Extract revision info
        rev_match = re.search(r"revision\s*=\s*['\"]([^'\"]+)['\"]", content)
        down_rev_match = re.search(r"down_revision\s*=\s*['\"]([^'\"]+)['\"]", content)
        
        rev = rev_match.group(1)[:12] if rev_match else "unknown"
        down_rev = down_rev_match.group(1)[:12] if down_rev_match else "None"
        
        print(f"  {rev} ← {down_rev}  {migration.name}")
    
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Alembic migration helper"
    )
    parser.add_argument(
        "command",
        choices=["check", "status", "safety", "history"],
        help="Command to run"
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Migration file path (for check/safety commands)"
    )
    parser.add_argument(
        "--migrations-dir",
        default="alembic/versions",
        help="Migrations directory (default: alembic/versions)"
    )
    
    args = parser.parse_args()
    
    migrations_dir = Path(args.migrations_dir)
    
    if args.command == "status":
        show_status(migrations_dir)
    
    elif args.command == "history":
        show_history(migrations_dir)
    
    elif args.command == "check":
        if not args.file:
            # Check all migrations
            migrations = find_migrations(migrations_dir)
            print(f"\n🔍 Checking {len(migrations)} migrations...")
            print("=" * 60)
            
            for migration in migrations:
                issues = check_migration(migration)
                if issues:
                    print(f"\n{migration.name}:")
                    for issue in issues:
                        print(f"  {issue}")
            
            print("\n✅ Check complete")
        else:
            file_path = Path(args.file)
            issues = check_migration(file_path)
            
            print(f"\n🔍 Checking: {file_path.name}")
            print("=" * 60)
            
            if issues:
                for issue in issues:
                    print(f"  {issue}")
            else:
                print("  ✅ No issues found")
    
    elif args.command == "safety":
        if not args.file:
            print("❌ Error: --file required for safety check")
            sys.exit(1)
        
        file_path = Path(args.file)
        result = check_safety(file_path)
        
        print(f"\n🛡️  Safety Check: {file_path.name}")
        print("=" * 60)
        
        if result["safe"] and not result["warnings"]:
            print("  ✅ Safe to run in production")
        elif result["safe"]:
            print("  ⚠️  Safe but has warnings:")
            for warning in result["warnings"]:
                print(f"     - {warning}")
        else:
            print("  ❌ NOT SAFE for production:")
            for op in result["blocking_operations"]:
                print(f"     - {op}")
        
        if result["recommendations"]:
            print("\n  💡 Recommendations:")
            for rec in result["recommendations"]:
                print(f"     - {rec}")
        
        sys.exit(0 if result["safe"] else 1)


if __name__ == "__main__":
    main()
