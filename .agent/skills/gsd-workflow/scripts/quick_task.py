#!/usr/bin/env python3
"""
Quick task execution with GSD guarantees.
For ad-hoc tasks: bug fixes, small features, config changes.
"""

import argparse
import re
import subprocess
from datetime import datetime
from pathlib import Path


def sanitize_filename(name: str) -> str:
    """Convert task description to safe filename."""
    # Remove special chars, keep alphanumeric and hyphens
    safe = re.sub(r'[^\w\s-]', '', name.lower())
    # Replace spaces with hyphens
    safe = re.sub(r'\s+', '-', safe.strip())
    # Limit length
    return safe[:50]


def create_quick_plan(planning_dir: Path, task_desc: str, full: bool = False) -> Path:
    """Create a quick task plan."""
    quick_dir = planning_dir / "quick"
    quick_dir.mkdir(exist_ok=True)
    
    # Find next quick task number
    existing = list(quick_dir.glob("[0-9]*-*.md"))
    next_num = len(existing) + 1
    
    safe_name = sanitize_filename(task_desc)
    plan_file = quick_dir / f"{next_num:03d}-{safe_name}-PLAN.md"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    plan_content = f"""<!-- Quick Task: {next_num:03d} -->
<quick-task created="{timestamp}">
  <description>{task_desc}</description>
  
  <tasks>
    <task type="auto" priority="1">
      <name>{task_desc}</name>
      <action>
TODO: Break down the specific steps needed
      </action>
      <verify>How to verify completion</verify>
      <done>Task complete when...</done>
    </task>
  </tasks>
</quick-task>
"""
    
    plan_file.write_text(plan_content)
    return plan_file


def create_summary(plan_file: Path, task_desc: str) -> Path:
    """Create a summary after execution."""
    summary_file = plan_file.with_name(plan_file.name.replace("-PLAN.md", "-SUMMARY.md"))
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    summary_content = f"""# Quick Task Summary: {task_desc}

**Completed**: {timestamp}

## What Was Done

<!-- Describe what was implemented -->

## Changes Made

- File: `path/to/file` - Description of change
- File: `path/to/file` - Description of change

## Verification

<!-- How was this verified? -->

- [ ] Manual test passed
- [ ] Related tests pass
- [ ] No regressions

## Notes

<!-- Any additional notes or follow-up items -->
"""
    
    summary_file.write_text(summary_content)
    return summary_file


def commit_changes(task_desc: str) -> bool:
    """Commit changes with GSD-style commit message."""
    try:
        # Check if there are changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        
        if not result.stdout.strip():
            print("   No changes to commit.")
            return True
        
        # Create commit
        safe_desc = task_desc[:50] if len(task_desc) > 50 else task_desc
        commit_msg = f"fix(quick): {safe_desc.lower()}"
        
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        
        print(f"   ✅ Committed: {commit_msg}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️  Commit failed: {e}")
        return False
    except FileNotFoundError:
        print("   ⚠️  Git not found. Skipping commit.")
        return False


def run_quick_task(project_dir: str, task_desc: str, full: bool = False) -> None:
    """Execute a quick task with GSD structure."""
    project_path = Path(project_dir).resolve()
    planning_dir = project_path / ".planning"
    
    # Ensure GSD is initialized
    if not planning_dir.exists():
        print("❌ GSD not initialized.")
        print(f"   Run: python3 .agent/skills/gsd-workflow/scripts/init_gsd.py --dir {project_dir}")
        return
    
    print("=" * 60)
    print("⚡ GSD QUICK TASK")
    print("=" * 60)
    print(f"Task: {task_desc}")
    print()
    
    # Create quick plan
    print("📝 Creating plan...")
    plan_file = create_quick_plan(planning_dir, task_desc, full)
    print(f"   Created: {plan_file.relative_to(project_path)}")
    print()
    
    # Instructions for Kimi
    print("🚀 NEXT STEPS FOR KIMI")
    print("-" * 40)
    print()
    print("1. Read the plan file:")
    print(f"   {plan_file}")
    print()
    print("2. Break down the task into specific steps")
    print("3. Implement the changes")
    print("4. Update the plan file with actual steps taken")
    print("5. Create summary file")
    print()
    
    if full:
        print("6. Verify the work (full mode)")
        print("7. Commit with: git commit -m 'fix(quick): {task}'")
    else:
        print("6. Commit the changes")
    
    print()
    print("💡 TIP: Quick tasks skip research and plan-checking.")
    print("   Use full GSD phases for complex features.")
    print()
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Quick task execution with GSD guarantees"
    )
    parser.add_argument("task", help="Task description")
    parser.add_argument("--dir", default=".", help="Project directory (default: current)")
    parser.add_argument(
        "--full", 
        action="store_true", 
        help="Full mode with verification (slower, more thorough)"
    )
    
    args = parser.parse_args()
    run_quick_task(args.dir, args.task, args.full)


if __name__ == "__main__":
    main()
