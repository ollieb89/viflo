#!/usr/bin/env python3
"""
Validate GSD plan files for correct XML structure and content.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple


class PlanValidator:
    """Validator for GSD plan XML structure."""
    
    REQUIRED_TASK_FIELDS = ["name", "action"]
    OPTIONAL_TASK_FIELDS = ["files", "verify", "done"]
    VALID_TASK_TYPES = ["auto", "manual"]
    VALID_PRIORITIES = ["1", "2", "3"]
    
    def __init__(self, plan_path: Path):
        self.plan_path = plan_path
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self) -> bool:
        """Run all validations. Returns True if valid."""
        if not self.plan_path.exists():
            self.errors.append(f"File not found: {self.plan_path}")
            return False
        
        content = self.plan_path.read_text()
        
        # Basic structure checks
        self._check_xml_structure(content)
        self._check_required_elements(content)
        self._check_tasks(content)
        self._check_size_limits(content)
        self._check_best_practices(content)
        
        return len(self.errors) == 0
    
    def _check_xml_structure(self, content: str) -> None:
        """Check basic XML structure."""
        # Check for plan root element
        if not re.search(r'<plan\s+phase="\d+"\s+plan="\d+">', content):
            self.errors.append("Missing or malformed <plan phase=\"N\" plan=\"M\"> root element")
        
        # Check closing tag
        if "</plan>" not in content:
            self.errors.append("Missing closing </plan> tag")
        
        # Check for unclosed tags (simple check)
        open_tags = re.findall(r'<(\w+)[^>]*(?<!/)>', content)
        close_tags = re.findall(r'</(\w+)>', content)
        
        # Self-closing tags
        self_closing = re.findall(r'<(\w+)[^>]*/>', content)
        
        # Count mismatches (very basic)
        for tag in set(open_tags):
            if tag in ['task', 'br', 'hr']:  # Self-closing allowed
                continue
            open_count = open_tags.count(tag)
            close_count = close_tags.count(tag)
            if open_count != close_count:
                self.errors.append(f"Unbalanced tags: <{tag}> opened {open_count} times, closed {close_count} times")
    
    def _check_required_elements(self, content: str) -> None:
        """Check for required plan elements."""
        if "<overview>" not in content:
            self.errors.append("Missing <overview> section")
        
        if "<tasks>" not in content:
            self.errors.append("Missing <tasks> section")
        
        # Check overview sub-elements
        if "<phase_name>" not in content:
            self.warnings.append("Missing <phase_name> in overview")
        
        if "<goal>" not in content:
            self.warnings.append("Missing <goal> in overview")
    
    def _check_tasks(self, content: str) -> None:
        """Validate task definitions."""
        # Find all task elements
        task_pattern = r'<task\s+type="(\w+)"\s+priority="(\d+)"[^>]*>'
        tasks = re.findall(task_pattern, content)
        
        if not tasks:
            self.errors.append("No tasks found in plan")
            return
        
        for i, (task_type, priority) in enumerate(tasks, 1):
            if task_type not in self.VALID_TASK_TYPES:
                self.errors.append(f"Task {i}: Invalid type '{task_type}'. Use 'auto' or 'manual'")
            
            if priority not in self.VALID_PRIORITIES:
                self.warnings.append(f"Task {i}: Unusual priority '{priority}'. Use 1 (blocking), 2 (important), or 3 (nice-to-have)")
        
        # Check for task content
        task_content_pattern = r'<task[^>]*>(.*?)</task>'
        task_contents = re.findall(task_content_pattern, content, re.DOTALL)
        
        for i, task_content in enumerate(task_contents, 1):
            for field in self.REQUIRED_TASK_FIELDS:
                if f"<{field}>" not in task_content:
                    self.errors.append(f"Task {i}: Missing <{field}>")
            
            # Check for empty action
            action_match = re.search(r'<action>(.*?)</action>', task_content, re.DOTALL)
            if action_match:
                action_content = action_match.group(1).strip()
                if action_content in ['', 'TODO', 'TODO:']:
                    self.warnings.append(f"Task {i}: Action is empty or placeholder")
    
    def _check_size_limits(self, content: str) -> None:
        """Check plan size limits."""
        lines = content.split('\n')
        line_count = len(lines)
        
        if line_count > 150:
            self.warnings.append(f"Plan is {line_count} lines (recommended: < 150). Consider splitting into multiple plans.")
        
        # Check individual task sizes
        task_pattern = r'<task[^>]*>(.*?)</task>'
        task_contents = re.findall(task_pattern, content, re.DOTALL)
        
        for i, task_content in enumerate(task_contents, 1):
            task_lines = task_content.count('\n')
            if task_lines > 50:
                self.warnings.append(f"Task {i} is {task_lines} lines (recommended: < 50). Consider breaking into smaller tasks.")
    
    def _check_best_practices(self, content: str) -> None:
        """Check for best practices."""
        # Check for verify steps
        if "<verify>" not in content:
            self.warnings.append("No verification steps found. Add <verify> to tasks.")
        
        # Check for dependencies section
        if "<dependencies>" not in content:
            self.warnings.append("No <dependencies> section. Add if this plan depends on others.")
        
        # Check for done criteria in auto tasks
        auto_tasks = re.findall(r'<task\s+type="auto"[^>]*>(.*?)</task>', content, re.DOTALL)
        for i, task in enumerate(auto_tasks, 1):
            if "<done>" not in task:
                self.warnings.append(f"Auto task {i}: Missing <done> criteria (completion definition)")
    
    def report(self) -> None:
        """Print validation report."""
        print(f"\n{'='*60}")
        print(f"📋 Plan Validation: {self.plan_path.name}")
        print(f"{'='*60}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ Plan is valid!")
        elif not self.errors:
            print("\n✅ Plan structure is valid (with warnings)")
        else:
            print("\n❌ Plan has errors that need fixing")
        
        print(f"{'='*60}\n")


def validate_all_plans(planning_dir: Path) -> None:
    """Validate all plan files in the planning directory."""
    plan_files = sorted(planning_dir.glob("*-*-PLAN.md"))
    quick_plans = sorted((planning_dir / "quick").glob("*-PLAN.md")) if (planning_dir / "quick").exists() else []
    
    all_plans = plan_files + quick_plans
    
    if not all_plans:
        print("No plan files found.")
        return
    
    print(f"\nFound {len(all_plans)} plan file(s)")
    
    total_errors = 0
    total_warnings = 0
    
    for plan_file in all_plans:
        validator = PlanValidator(plan_file)
        validator.validate()
        validator.report()
        total_errors += len(validator.errors)
        total_warnings += len(validator.warnings)
    
    print(f"\n{'='*60}")
    print(f"SUMMARY: {len(all_plans)} plans, {total_errors} errors, {total_warnings} warnings")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Validate GSD plan files")
    parser.add_argument("plan", nargs="?", help="Specific plan file to validate")
    parser.add_argument("--dir", default=".", help="Project directory (default: current)")
    parser.add_argument("--all", action="store_true", help="Validate all plans in .planning/")
    
    args = parser.parse_args()
    
    project_path = Path(args.dir).resolve()
    planning_dir = project_path / ".planning"
    
    if not planning_dir.exists():
        print(f"❌ GSD not initialized in {project_path}")
        return 1
    
    if args.all or not args.plan:
        validate_all_plans(planning_dir)
    else:
        plan_path = planning_dir / args.plan
        if not plan_path.exists():
            # Try quick directory
            plan_path = planning_dir / "quick" / args.plan
        
        validator = PlanValidator(plan_path)
        is_valid = validator.validate()
        validator.report()
        return 0 if is_valid else 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
