#!/usr/bin/env python3
"""
Helper for creating GSD-style atomic commits.
Follows conventional commits format with GSD metadata.
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple


COMMIT_TYPES = {
    "feat": "New feature",
    "fix": "Bug fix",
    "docs": "Documentation",
    "style": "Formatting, missing semi colons, etc",
    "refactor": "Code refactoring",
    "test": "Adding tests",
    "chore": "Build process, dependencies, etc",
    "plan": "Planning documents",
    "research": "Research documentation",
}


def get_git_info() -> Tuple[str, str]:
    """Get current branch and last commit."""
    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True
        ).stdout.strip()
        
        last_commit = subprocess.run(
            ["git", "log", "-1", "--pretty=%s"],
            capture_output=True, text=True, check=True
        ).stdout.strip()
        
        return branch, last_commit
    except subprocess.CalledProcessError:
        return "unknown", "unknown"


def get_changed_files() -> list:
    """Get list of changed files."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, check=True
        )
        
        files = []
        for line in result.stdout.strip().split('\n'):
            if line:
                status = line[:2].strip()
                filepath = line[3:]
                files.append((status, filepath))
        
        return files
    except subprocess.CalledProcessError:
        return []


def suggest_commit_type(files: list) -> str:
    """Suggest commit type based on changed files."""
    file_paths = ' '.join([f[1] for f in files]).lower()
    
    # Check for planning documents
    if any(x in file_paths for x in ['.planning/', 'project.md', 'requirements.md', 'roadmap.md', 'plan.md']):
        return "plan"
    
    # Check for tests
    if any(x in file_paths for x in ['test', 'spec']):
        return "test"
    
    # Check for docs
    if any(x in file_paths for x in ['.md', 'readme', 'docs/']):
        return "docs"
    
    # Check for config/build files
    if any(x in file_paths for x in ['package.json', 'tsconfig', 'eslint', 'prettier', 'dockerfile', 'makefile']):
        return "chore"
    
    # Default to feat for source files
    if any(x in file_paths for x in ['.ts', '.tsx', '.js', '.jsx', '.py', '.go', '.rs']):
        return "feat"
    
    return "chore"


def suggest_scope(files: list) -> Optional[str]:
    """Suggest commit scope based on changed files."""
    # Extract common directories
    dirs = set()
    for _, filepath in files:
        parts = filepath.split('/')
        if len(parts) > 1:
            dirs.add(parts[0])
    
    # Common scope mappings
    scope_mappings = {
        'src': 'core',
        'components': 'ui',
        'app': 'app',
        'api': 'api',
        'lib': 'lib',
        'utils': 'utils',
        'styles': 'styles',
        'public': 'assets',
        'tests': 'tests',
        'scripts': 'scripts',
        'docs': 'docs',
        '.planning': 'planning',
    }
    
    for dir_name, scope in scope_mappings.items():
        if dir_name in dirs:
            return scope
    
    # Try to find phase number from plan files
    for _, filepath in files:
        match = re.search(r'(\d+)-.*-PLAN\.md', filepath)
        if match:
            return f"phase-{match.group(1)}"
    
    return None


def create_gsd_commit_message(
    commit_type: str,
    scope: Optional[str],
    description: str,
    phase: Optional[str] = None,
    task: Optional[str] = None,
    breaking: bool = False
) -> str:
    """Create a GSD-style commit message."""
    # Build header
    scope_part = f"({scope})" if scope else ""
    breaking_marker = "!" if breaking else ""
    
    header = f"{commit_type}{scope_part}{breaking_marker}: {description}"
    
    # Build body with GSD metadata
    body_parts = []
    
    if phase:
        body_parts.append(f"Phase: {phase}")
    if task:
        body_parts.append(f"Task: {task}")
    
    if body_parts:
        body = "\n".join(body_parts)
        return f"{header}\n\n{body}"
    
    return header


def interactive_commit() -> str:
    """Interactive commit creation."""
    print("\n📝 GSD Commit Helper\n")
    
    # Show changed files
    files = get_changed_files()
    if not files:
        print("❌ No changes to commit.")
        return ""
    
    print("Changed files:")
    for status, filepath in files:
        status_icon = {"M": "📝", "A": "➕", "D": "🗑️", "??": "❓"}.get(status, "•")
        print(f"  {status_icon} {filepath}")
    print()
    
    # Suggest and confirm type
    suggested_type = suggest_commit_type(files)
    print(f"Select commit type (suggested: {suggested_type}):")
    for key, desc in COMMIT_TYPES.items():
        marker = " →" if key == suggested_type else "  "
        print(f"{marker} {key:10} - {desc}")
    
    commit_type = input(f"\nType [{suggested_type}]: ").strip() or suggested_type
    
    # Suggest and confirm scope
    suggested_scope = suggest_scope(files)
    scope_input = input(f"Scope [{suggested_scope or 'none'}]: ").strip()
    scope = scope_input if scope_input else suggested_scope
    if scope == "none":
        scope = None
    
    # Get description
    description = input("Description: ").strip()
    while not description:
        print("❌ Description is required")
        description = input("Description: ").strip()
    
    # Check for phase/task info
    phase = None
    task = None
    
    # Try to extract from files
    for _, filepath in files:
        match = re.search(r'(\d+)-(\d+)-PLAN\.md', filepath)
        if match:
            phase = match.group(1)
            task = match.group(2)
            break
        match = re.search(r'(\d+)-.*-PLAN\.md', filepath)
        if match:
            phase = match.group(1)
            break
    
    if phase:
        phase_input = input(f"Phase [{phase}]: ").strip()
        phase = phase_input if phase_input else phase
    
    # Create message
    message = create_gsd_commit_message(commit_type, scope, description, phase, task)
    
    print(f"\n{'='*60}")
    print("Commit message preview:")
    print(f"{'='*60}")
    print(message)
    print(f"{'='*60}\n")
    
    confirm = input("Create this commit? [Y/n]: ").strip().lower()
    if confirm in ['', 'y', 'yes']:
        return message
    else:
        print("Aborted.")
        return ""


def commit(message: str, dry_run: bool = False) -> bool:
    """Execute git commit."""
    if not message:
        return False
    
    if dry_run:
        print("\n🔍 DRY RUN - Would execute:")
        print(f"  git add -A")
        print(f'  git commit -m "{message[:50]}..."')
        return True
    
    try:
        # Add all changes
        subprocess.run(["git", "add", "-A"], check=True)
        
        # Create commit
        subprocess.run(["git", "commit", "-m", message], check=True)
        
        print("\n✅ Commit created successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Commit failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="GSD-style commit helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Interactive mode
  %(prog)s -m "fix auth bug"         # Quick commit
  %(prog)s -t fix -s auth -m "bug"   # Specify type and scope
  %(prog)s --dry-run                 # Preview without committing
        """
    )
    
    parser.add_argument("-m", "--message", help="Commit description")
    parser.add_argument("-t", "--type", choices=list(COMMIT_TYPES.keys()), help="Commit type")
    parser.add_argument("-s", "--scope", help="Commit scope")
    parser.add_argument("-p", "--phase", help="Phase number (for GSD tracking)")
    parser.add_argument("--task", help="Task number (for GSD tracking)")
    parser.add_argument("--breaking", action="store_true", help="Breaking change")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, don't commit")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode (default)")
    
    args = parser.parse_args()
    
    # Check if we're in a git repo
    try:
        subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Not a git repository or git not found")
        return 1
    
    # Determine mode
    if args.message:
        # Non-interactive mode
        commit_type = args.type or suggest_commit_type(get_changed_files())
        scope = args.scope
        message = create_gsd_commit_message(
            commit_type, scope, args.message,
            args.phase, args.task, args.breaking
        )
    else:
        # Interactive mode
        message = interactive_commit()
    
    if message:
        success = commit(message, args.dry_run)
        return 0 if success else 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
