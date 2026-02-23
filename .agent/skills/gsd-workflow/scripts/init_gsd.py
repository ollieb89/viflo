#!/usr/bin/env python3
"""
Initialize GSD (Get Shit Done) structure in a project.
Creates .planning/ directory with initial artifacts.
"""

import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path


def get_template(skill_dir: Path, name: str) -> str:
    """Read a template file from the skill's assets."""
    template_path = skill_dir / "assets" / "templates" / f"{name}.md"
    if template_path.exists():
        return template_path.read_text()
    return f"# {name}\n\n<!-- Template not found -->\n"


def init_gsd(project_dir: str, auto: bool = False) -> None:
    """Initialize GSD structure in the project directory."""
    project_path = Path(project_dir).resolve()
    planning_dir = project_path / ".planning"
    
    # Find skill directory (this script is in .agent/skills/gsd-workflow/scripts/)
    script_dir = Path(__file__).parent.resolve()
    skill_dir = script_dir.parent
    
    # Create .planning directory structure
    planning_dir.mkdir(exist_ok=True)
    (planning_dir / "research").mkdir(exist_ok=True)
    (planning_dir / "todos").mkdir(exist_ok=True)
    
    # Create initial artifacts from templates
    artifacts = {
        "PROJECT.md": get_template(skill_dir, "PROJECT"),
        "REQUIREMENTS.md": get_template(skill_dir, "REQUIREMENTS"),
        "ROADMAP.md": get_template(skill_dir, "ROADMAP"),
        "STATE.md": get_template(skill_dir, "STATE"),
    }
    
    created = []
    skipped = []
    
    for filename, content in artifacts.items():
        filepath = planning_dir / filename
        if filepath.exists():
            skipped.append(filename)
        else:
            filepath.write_text(content)
            created.append(filename)
    
    # Create config.json
    config_path = planning_dir / "config.json"
    if not config_path.exists():
        config = '''{
  "mode": "interactive",
  "depth": "standard",
  "profile": "balanced",
  "workflow": {
    "research": true,
    "plan_check": true,
    "verifier": true,
    "auto_advance": false
  },
  "parallelization": {
    "enabled": true
  },
  "git": {
    "commit_docs": true,
    "branching_strategy": "none"
  }
}'''
        config_path.write_text(config)
        created.append("config.json")
    else:
        skipped.append("config.json")
    
    # Print results
    print(f"GSD initialized in: {planning_dir}")
    print()
    if created:
        print("Created:")
        for f in created:
            print(f"  ✓ {f}")
    if skipped:
        print("Skipped (already exist):")
        for f in skipped:
            print(f"  • {f}")
    print()
    print("Next steps:")
    print("  1. Edit PROJECT.md with your project vision")
    print("  2. Edit REQUIREMENTS.md with v1/v2 requirements")
    print("  3. Run: gsd discuss 1  (to plan phase 1)")


def main():
    parser = argparse.ArgumentParser(description="Initialize GSD structure")
    parser.add_argument("--dir", default=".", help="Project directory (default: current)")
    parser.add_argument("--auto", action="store_true", help="Auto mode (minimal questions)")
    
    args = parser.parse_args()
    init_gsd(args.dir, args.auto)


if __name__ == "__main__":
    main()
