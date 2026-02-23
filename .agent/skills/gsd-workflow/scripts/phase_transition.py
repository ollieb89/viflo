#!/usr/bin/env python3
"""
Phase Transition Helper: Manage state changes between GSD phases.
Handles completing one phase and moving to the next.
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class PhaseManager:
    """Manage phase lifecycle and transitions."""
    
    VALID_STATES = [
        "not-started",
        "discussing",
        "planning",
        "ready-to-execute",
        "executing",
        "verifying",
        "complete"
    ]
    
    def __init__(self, planning_dir: Path):
        self.planning_dir = planning_dir
        self.state_file = planning_dir / "STATE.md"
        self.roadmap_file = planning_dir / "ROADMAP.md"
    
    def get_current_phase(self) -> Optional[int]:
        """Get the current active phase from roadmap."""
        if not self.roadmap_file.exists():
            return None
        
        content = self.roadmap_file.read_text()
        
        # Find first non-complete phase
        for match in re.finditer(r'## Phase (\d+):[^\n]*\n[^#]*?\*\*Status\*\*:\s*(\w+)', content, re.DOTALL):
            phase_num = int(match.group(1))
            status = match.group(2).lower()
            
            if status != "complete":
                return phase_num
        
        return None
    
    def get_phase_status(self, phase: int) -> str:
        """Get status of a specific phase."""
        if not self.roadmap_file.exists():
            return "unknown"
        
        content = self.roadmap_file.read_text()
        pattern = rf'## Phase {phase}:[^\n]*\n[^#]*?\*\*Status\*\*:\s*(\w+)'
        match = re.search(pattern, content, re.DOTALL)
        
        return match.group(1).lower() if match else "unknown"
    
    def update_phase_status(self, phase: int, new_status: str) -> bool:
        """Update phase status in roadmap."""
        if not self.roadmap_file.exists():
            print(f"❌ ROADMAP.md not found")
            return False
        
        if new_status not in self.VALID_STATES:
            print(f"❌ Invalid status: {new_status}")
            print(f"   Valid: {', '.join(self.VALID_STATES)}")
            return False
        
        content = self.roadmap_file.read_text()
        
        # Update status line
        pattern = rf'(## Phase {phase}:.*?(?:\n|\r)\s*\*\*Status\*\*:\s*)\w+'
        replacement = rf'\g<1>{new_status}'
        
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        if new_content == content:
            print(f"⚠️  Phase {phase} not found in ROADMAP.md")
            return False
        
        self.roadmap_file.write_text(new_content)
        return True
    
    def update_state_file(self, phase: int, status: str, note: str = "") -> bool:
        """Update STATE.md with current phase info."""
        if not self.state_file.exists():
            print(f"❌ STATE.md not found")
            return False
        
        content = self.state_file.read_text()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Update current phase and status
        content = re.sub(
            r'\*\*Phase\*\*:.*',
            f'**Phase**: {phase}',
            content
        )
        content = re.sub(
            r'\*\*Status\*\*:.*',
            f'**Status**: {status}',
            content
        )
        
        # Add session entry
        session_entry = f"\n### {timestamp}\n\n"
        session_entry += f"**Phase {phase}**: {status}\n"
        if note:
            session_entry += f"\n{note}\n"
        
        # Insert after "## Session Memory" or at end
        if "## Session Memory" in content:
            parts = content.split("## Session Memory")
            content = parts[0] + "## Session Memory" + session_entry + parts[1]
        
        self.state_file.write_text(content)
        return True
    
    def get_plan_files(self, phase: int) -> list:
        """Get all plan files for a phase."""
        pattern = f"{phase}-*-PLAN.md"
        return sorted(self.planning_dir.glob(pattern))
    
    def get_summary_files(self, phase: int) -> list:
        """Get all summary files for a phase."""
        pattern = f"{phase}-*-SUMMARY.md"
        return sorted(self.planning_dir.glob(pattern))
    
    def check_phase_completion(self, phase: int) -> dict:
        """Check if phase is ready for completion."""
        plans = self.get_plan_files(phase)
        summaries = self.get_summary_files(phase)
        
        results = {
            "plans_total": len(plans),
            "plans_completed": len(summaries),
            "all_complete": len(plans) > 0 and len(plans) == len(summaries),
            "missing_summaries": []
        }
        
        plan_names = {p.name.replace("-PLAN.md", "") for p in plans}
        summary_names = {s.name.replace("-SUMMARY.md", "") for s in summaries}
        
        results["missing_summaries"] = list(plan_names - summary_names)
        
        return results
    
    def complete_phase(self, phase: int, commit: bool = True) -> bool:
        """Mark phase as complete and optionally commit."""
        check = self.check_phase_completion(phase)
        
        if not check["all_complete"]:
            print(f"❌ Phase {phase} not ready for completion")
            print(f"   Plans: {check['plans_completed']}/{check['plans_total']} complete")
            if check["missing_summaries"]:
                print(f"   Missing summaries: {', '.join(check['missing_summaries'])}")
            return False
        
        # Update roadmap
        if not self.update_phase_status(phase, "complete"):
            return False
        
        # Update state
        self.update_state_file(phase, "complete", f"Phase {phase} completed")
        
        # Commit if requested
        if commit:
            try:
                subprocess.run(["git", "add", "-A"], check=True, cwd=self.planning_dir.parent)
                subprocess.run(
                    ["git", "commit", "-m", f"docs: complete phase {phase}"],
                    check=True,
                    cwd=self.planning_dir.parent
                )
                print(f"   ✅ Changes committed")
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️  Commit failed: {e}")
        
        return True
    
    def start_phase(self, phase: int) -> bool:
        """Initialize a new phase."""
        # Check if previous phase is complete
        if phase > 1:
            prev_status = self.get_phase_status(phase - 1)
            if prev_status != "complete":
                print(f"⚠️  Phase {phase-1} is not complete (status: {prev_status})")
                response = input("   Start phase anyway? [y/N]: ").strip().lower()
                if response not in ['y', 'yes']:
                    return False
        
        # Update status to discussing
        self.update_phase_status(phase, "discussing")
        self.update_state_file(phase, "discussing", f"Started phase {phase}")
        
        return True


def print_status(manager: PhaseManager) -> None:
    """Print current phase status."""
    current = manager.get_current_phase()
    
    print(f"\n{'='*60}")
    print("📊 PHASE STATUS")
    print(f"{'='*60}\n")
    
    if current:
        status = manager.get_phase_status(current)
        check = manager.check_phase_completion(current)
        
        print(f"Current Phase: {current}")
        print(f"Status: {status}")
        print(f"Progress: {check['plans_completed']}/{check['plans_total']} plans complete")
        
        if check["missing_summaries"]:
            print(f"\nIncomplete plans:")
            for plan in check["missing_summaries"]:
                print(f"   • {plan}")
        
        # Show next action
        print(f"\n🚀 NEXT ACTION:")
        if status == "not-started":
            print(f"   Run: gsd discuss {current}")
        elif status == "discussing":
            print(f"   Run: gsd plan {current}")
        elif status == "planning":
            print(f"   Run: gsd execute {current}")
        elif status == "executing":
            if check["all_complete"]:
                print(f"   Ready to verify!")
            else:
                print(f"   Continue executing plans")
        elif status == "verifying":
            print(f"   Run: gsd verify {current}")
    else:
        print("✅ All phases complete!")
    
    print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Phase Transition Helper: Manage GSD phase lifecycle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                    # Show current phase status
  %(prog)s start 2                   # Start phase 2
  %(prog)s complete 1                # Mark phase 1 as complete
  %(prog)s set-status 2 executing    # Set phase 2 status to executing
        """
    )
    
    parser.add_argument("action", choices=["status", "start", "complete", "set-status", "check"],
                        help="Action to perform")
    parser.add_argument("phase", type=int, nargs="?", help="Phase number")
    parser.add_argument("status_value", nargs="?", help="New status (for set-status)")
    parser.add_argument("--dir", default=".", help="Project directory (default: current)")
    parser.add_argument("--no-commit", action="store_true", help="Don't commit changes")
    
    args = parser.parse_args()
    
    project_path = Path(args.dir).resolve()
    planning_dir = project_path / ".planning"
    
    if not planning_dir.exists():
        print(f"❌ GSD not initialized in {project_path}")
        return 1
    
    manager = PhaseManager(planning_dir)
    
    if args.action == "status":
        print_status(manager)
        return 0
    
    if args.action == "check":
        if not args.phase:
            # Check all phases
            for phase in range(1, 20):  # Reasonable upper limit
                status = manager.get_phase_status(phase)
                if status == "unknown":
                    break
                check = manager.check_phase_completion(phase)
                icon = "✅" if check["all_complete"] else "⏳"
                print(f"{icon} Phase {phase}: {check['plans_completed']}/{check['plans_total']} complete ({status})")
        else:
            check = manager.check_phase_completion(args.phase)
            print(f"Phase {args.phase}:")
            print(f"  Plans: {check['plans_completed']}/{check['plans_total']} complete")
            if check["missing_summaries"]:
                print(f"  Missing: {', '.join(check['missing_summaries'])}")
        return 0
    
    if args.action in ["start", "complete", "set-status"] and not args.phase:
        print(f"❌ Phase number required for {args.action}")
        return 1
    
    if args.action == "start":
        if manager.start_phase(args.phase):
            print(f"✅ Phase {args.phase} started")
            print(f"   Status: discussing")
            print(f"\n   Next: gsd discuss {args.phase}")
        else:
            return 1
    
    elif args.action == "complete":
        if manager.complete_phase(args.phase, commit=not args.no_commit):
            print(f"✅ Phase {args.phase} marked as complete")
            
            # Suggest next phase
            next_phase = args.phase + 1
            next_status = manager.get_phase_status(next_phase)
            if next_status != "unknown":
                print(f"\n   Next: gsd discuss {next_phase}")
        else:
            return 1
    
    elif args.action == "set-status":
        if not args.status_value:
            print("❌ Status value required")
            return 1
        
        if manager.update_phase_status(args.phase, args.status_value):
            manager.update_state_file(args.phase, args.status_value)
            print(f"✅ Phase {args.phase} status updated to: {args.status_value}")
        else:
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
