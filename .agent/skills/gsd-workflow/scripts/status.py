#!/usr/bin/env python3
"""
Show GSD project status - current phase, progress, and next steps.
"""

import argparse
import json
import re
from pathlib import Path
from typing import Optional


def parse_roadmap(planning_dir: Path) -> dict:
    """Parse ROADMAP.md to extract phase statuses."""
    roadmap_path = planning_dir / "ROADMAP.md"
    if not roadmap_path.exists():
        return {"phases": [], "current": None}
    
    content = roadmap_path.read_text()
    phases = []
    current_phase = None
    
    # Parse phase headers
    phase_pattern = r'## Phase (\d+):([^\n]+)\n\s*\*\*Goal\*\*:[^\n]*\n\s*\*\*Requirements\*\*:([^\n]*)\n\s*\*\*Status\*\*:([^\n]*)'
    
    for match in re.finditer(phase_pattern, content, re.MULTILINE):
        num = int(match.group(1))
        name = match.group(2).strip()
        reqs = match.group(3).strip()
        status = match.group(4).strip().lower()
        
        phases.append({
            "num": num,
            "name": name,
            "requirements": reqs,
            "status": status
        })
        
        # Find first non-complete phase as current
        if status != "complete" and current_phase is None:
            current_phase = num
    
    return {"phases": phases, "current": current_phase}


def parse_state(planning_dir: Path) -> dict:
    """Parse STATE.md for current status and blockers."""
    state_path = planning_dir / "STATE.md"
    if not state_path.exists():
        return {"status": "unknown", "blockers": []}
    
    content = state_path.read_text()
    
    # Extract current status
    status_match = re.search(r'\*\*Status\*\*:\s*([^\n]+)', content)
    status = status_match.group(1).strip() if status_match else "unknown"
    
    # Extract blockers
    blockers = []
    blockers_section = re.search(r'## Blockers\n\n([^#]+)', content)
    if blockers_section:
        blocker_lines = blockers_section.group(1).strip().split('\n')
        for line in blocker_lines:
            line = line.strip()
            if line.startswith('- [ ]'):
                blockers.append(line[5:].strip())
    
    return {"status": status, "blockers": blockers}


def find_plan_files(planning_dir: Path, phase: int) -> list:
    """Find all plan files for a phase."""
    pattern = f"{phase}-*-PLAN.md"
    return sorted(planning_dir.glob(pattern))


def find_summary_files(planning_dir: Path, phase: int) -> list:
    """Find all summary files for a phase."""
    pattern = f"{phase}-*-SUMMARY.md"
    return sorted(planning_dir.glob(pattern))


def count_todos(planning_dir: Path) -> int:
    """Count pending todos."""
    todos_dir = planning_dir / "todos"
    if not todos_dir.exists():
        return 0
    return len(list(todos_dir.glob("*.md")))


def show_status(project_dir: str) -> None:
    """Display project status."""
    project_path = Path(project_dir).resolve()
    planning_dir = project_path / ".planning"
    
    if not planning_dir.exists():
        print("❌ GSD not initialized in this project.")
        print(f"   Run: python3 .agent/skills/gsd-workflow/scripts/init_gsd.py --dir {project_dir}")
        return
    
    print("=" * 60)
    print("📊 GSD PROJECT STATUS")
    print("=" * 60)
    print(f"Project: {project_path.name}")
    print(f"Planning: {planning_dir}")
    print()
    
    # Parse roadmap
    roadmap = parse_roadmap(planning_dir)
    state = parse_state(planning_dir)
    
    # Show phases progress
    if roadmap["phases"]:
        print("📋 PHASES")
        print("-" * 40)
        
        complete = sum(1 for p in roadmap["phases"] if p["status"] == "complete")
        total = len(roadmap["phases"])
        
        for phase in roadmap["phases"]:
            status_icon = {
                "complete": "✅",
                "in-progress": "🔄",
                "planning": "📝",
                "discussing": "💬",
                "not-started": "⏳"
            }.get(phase["status"], "❓")
            
            current_marker = " →" if phase["num"] == roadmap["current"] else "  "
            print(f"{current_marker} {status_icon} Phase {phase['num']}: {phase['name']}")
        
        print()
        print(f"Progress: {complete}/{total} phases complete ({complete/total*100:.0f}%)")
        print()
    
    # Show current state
    if state["status"] != "unknown":
        print(f"🎯 Current State: {state['status'].upper()}")
        print()
    
    # Show blockers
    if state["blockers"]:
        print("⚠️  BLOCKERS")
        print("-" * 40)
        for blocker in state["blockers"]:
            print(f"   • {blocker}")
        print()
    
    # Show current phase details
    if roadmap["current"]:
        current = roadmap["current"]
        plans = find_plan_files(planning_dir, current)
        summaries = find_summary_files(planning_dir, current)
        
        print(f"📁 PHASE {current} DETAILS")
        print("-" * 40)
        print(f"   Plans: {len(plans)} total, {len(summaries)} complete")
        
        if plans:
            for plan in plans:
                done = any(s.name.replace("SUMMARY", "PLAN") == plan.name for s in summaries)
                icon = "✅" if done else "⏳"
                print(f"   {icon} {plan.name}")
        print()
    
    # Show todos
    todo_count = count_todos(planning_dir)
    if todo_count > 0:
        print(f"📝 Captured Todos: {todo_count}")
        print()
    
    # Show next steps
    print("🚀 NEXT STEPS")
    print("-" * 40)
    
    if not roadmap["phases"]:
        print("   1. Edit REQUIREMENTS.md to define your phases")
        print("   2. Edit ROADMAP.md with phase breakdown")
    elif state["blockers"]:
        print("   1. Resolve blockers listed above")
        print("   2. Continue with current phase")
    elif roadmap["current"]:
        current = roadmap["current"]
        phase_data = next((p for p in roadmap["phases"] if p["num"] == current), None)
        
        if phase_data:
            if phase_data["status"] == "not-started":
                print(f"   Run: gsd discuss {current}")
            elif phase_data["status"] == "discussing":
                print(f"   Run: gsd plan {current}")
            elif phase_data["status"] == "planning":
                print(f"   Run: gsd execute {current}")
            elif phase_data["status"] == "in-progress":
                print(f"   Run: gsd verify {current}")
            elif phase_data["status"] == "complete":
                next_phase = current + 1
                if any(p["num"] == next_phase for p in roadmap["phases"]):
                    print(f"   Run: gsd discuss {next_phase}")
                else:
                    print("   All phases complete! Run: gsd complete-milestone")
    else:
        print("   All phases complete!")
    
    print()
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Show GSD project status")
    parser.add_argument("--dir", default=".", help="Project directory (default: current)")
    
    args = parser.parse_args()
    show_status(args.dir)


if __name__ == "__main__":
    main()
