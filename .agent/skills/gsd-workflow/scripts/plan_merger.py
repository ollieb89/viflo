#!/usr/bin/env python3
"""
Plan Merger: Merge multiple small plans into one larger plan.
Useful when plans are too granular or need to be consolidated.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Dict



class PlanMerger:
    """Merge multiple GSD plans into one."""
    
    def __init__(self, planning_dir: Path):
        self.planning_dir = planning_dir
    
    def load_plan(self, filename: str) -> Dict:
        """Load and parse a plan file."""
        # Prevent path traversal - normalize and check it's within planning_dir
        filepath = (self.planning_dir / filename).resolve()
        if not str(filepath).startswith(str(self.planning_dir.resolve())):
            raise ValueError(f"Invalid plan path: {filename}")
        
        if not filepath.exists():
            raise FileNotFoundError(f"Plan not found: {filename}")
        
        content = filepath.read_text()
        
        return {
            "file": filename,
            "path": filepath,
            "content": content,
            "phase": self._extract_phase(content),
            "plan_num": self._extract_plan_num(content),
            "name": self._extract_name(content),
            "tasks": self._extract_tasks(content),
            "dependencies": self._extract_dependencies(content),
        }
    
    def _extract_phase(self, content: str) -> str:
        """Extract phase from plan tag."""
        match = re.search(r'<plan\s+phase="(\d+)"', content)
        return match.group(1) if match else "?"
    
    def _extract_plan_num(self, content: str) -> str:
        """Extract plan number from plan tag."""
        match = re.search(r'<plan\s+phase="\d+"\s+plan="(\d+)"', content)
        return match.group(1) if match else "?"
    
    def _extract_name(self, content: str) -> str:
        """Extract phase name."""
        match = re.search(r'<phase_name>([^<]+)</phase_name>', content)
        return match.group(1).strip() if match else "Unknown"
    
    def _extract_tasks(self, content: str) -> List[str]:
        """Extract task XML blocks."""
        tasks = []
        task_pattern = r'<task[^>]*>.*?</task>'
        for match in re.finditer(task_pattern, content, re.DOTALL):
            tasks.append(match.group(0))
        return tasks
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies."""
        deps = []
        deps_match = re.search(r'<dependencies>(.+?)</dependencies>', content, re.DOTALL)
        if deps_match:
            complete_deps = re.findall(r'<complete>(.+?)</complete>', deps_match.group(1), re.DOTALL)
            deps.extend(complete_deps)
        return deps
    
    def merge_plans(self, plan_files: List[str], new_plan_name: str) -> str:
        """Merge multiple plans into one."""
        plans = [self.load_plan(f) for f in plan_files]
        
        # Determine phase (all should be same)
        phases = set(p["phase"] for p in plans)
        if len(phases) > 1:
            print(f"⚠️  Plans are from different phases: {phases}")
            phase = sorted(phases)[0]
        else:
            phase = phases.pop()
        
        # Collect all tasks
        all_tasks = []
        all_dependencies = []
        
        for plan in plans:
            all_tasks.extend(plan["tasks"])
            all_dependencies.extend(plan["dependencies"])
        
        # Remove duplicate dependencies
        all_dependencies = list(dict.fromkeys(all_dependencies))
        
        # Renumber tasks by priority
        tasks_by_priority = {"1": [], "2": [], "3": []}
        for task in all_tasks:
            priority_match = re.search(r'<task\s+[^>]*priority="(\d)"', task)
            priority = priority_match.group(1) if priority_match else "2"
            tasks_by_priority.get(priority, tasks_by_priority["2"]).append(task)
        
        # Rebuild merged tasks with sequential numbering
        merged_tasks = []
        task_counter = 1
        
        for priority in ["1", "2", "3"]:
            for task in tasks_by_priority[priority]:
                # Update task numbering in name if present
                task_xml = re.sub(
                    r'(<name>)([^<]+)(</name>)',
                    lambda m: f"{m.group(1)}{task_counter:02d}. {m.group(2).strip()}{m.group(3)}",
                    task
                )
                merged_tasks.append(task_xml)
                task_counter += 1
        
        # Build merged plan
        lines = []
        lines.append(f"<plan phase=\"{phase}\" plan=\"MERGED\">")
        lines.append("  <overview>")
        lines.append(f"    <phase_name>{new_plan_name}</phase_name>")
        lines.append(f"    <goal>Merged from {len(plans)} plans</goal>")
        lines.append("  </overview>")
        lines.append("")
        
        # Merged from section
        lines.append("  <!-- Merged From -->")
        lines.append("  <merged_from>")
        for plan in plans:
            lines.append(f"    <plan file=\"{plan['file']}\">{plan['name']}</plan>")
        lines.append("  </merged_from>")
        lines.append("")
        
        # Dependencies
        if all_dependencies:
            lines.append("  <dependencies>")
            for dep in all_dependencies:
                lines.append(f"    <complete>{dep}</complete>")
            lines.append("  </dependencies>")
            lines.append("")
        
        # Tasks
        lines.append(f"  <tasks>")
        lines.append(f"    <!-- {len(merged_tasks)} tasks from {len(plans)} plans -->")
        lines.append("")
        
        for task in merged_tasks:
            # Indent task properly
            indented_task = '\n'.join('    ' + line for line in task.strip().split('\n'))
            lines.append(indented_task)
            lines.append("")
        
        lines.append("  </tasks>")
        lines.append("</plan>")
        
        return '\n'.join(lines)
    
    def split_plan(self, plan_file: str, split_after: List[int]) -> List[str]:
        """Split a large plan into multiple smaller plans."""
        plan = self.load_plan(plan_file)
        tasks = plan["tasks"]
        
        if not tasks:
            raise ValueError("No tasks found in plan")
        
        # Validate split points
        for point in split_after:
            if point < 1 or point >= len(tasks):
                raise ValueError(f"Invalid split point: {point}. Plan has {len(tasks)} tasks.")
        
        # Create split ranges
        split_points = sorted(split_after)
        ranges = []
        start = 0
        
        for point in split_points:
            ranges.append((start, point))
            start = point
        ranges.append((start, len(tasks)))
        
        # Generate new plans
        new_plans = []
        phase = plan["phase"]
        
        for i, (start_idx, end_idx) in enumerate(ranges, 1):
            task_subset = tasks[start_idx:end_idx]
            
            lines = []
            lines.append(f"<plan phase=\"{phase}\" plan=\"{i}\">")
            lines.append("  <overview>")
            lines.append(f"    <phase_name>{plan['name']} (Part {i})</phase_name>")
            lines.append(f"    <goal>Tasks {start_idx+1}-{end_idx} of original plan</goal>")
            lines.append("  </overview>")
            lines.append("")
            
            if i > 1:
                lines.append("  <dependencies>")
                lines.append(f"    <complete>Plan {i-1}</complete>")
                lines.append("  </dependencies>")
                lines.append("")
            
            lines.append("  <tasks>")
            for task in task_subset:
                indented_task = '\n'.join('    ' + line for line in task.strip().split('\n'))
                lines.append(indented_task)
                lines.append("")
            lines.append("  </tasks>")
            lines.append("</plan>")
            
            new_plans.append('\n'.join(lines))
        
        return new_plans
    
    def consolidate_quick_tasks(self) -> str:
        """Consolidate all quick tasks into a single summary plan."""
        quick_dir = self.planning_dir / "quick"
        if not quick_dir.exists():
            return None
        
        quick_plans = sorted(quick_dir.glob("*-PLAN.md"))
        if not quick_plans:
            return None
        
        all_tasks = []
        for plan_file in quick_plans:
            content = plan_file.read_text()
            tasks = self._extract_tasks(content)
            all_tasks.extend(tasks)
        
        # Build summary
        lines = []
        lines.append("<plan phase=\"QUICK\" plan=\"CONSOLIDATED\">")
        lines.append("  <overview>")
        lines.append("    <phase_name>Quick Tasks Summary</phase_name>")
        lines.append(f"    <goal>Consolidated {len(quick_plans)} quick tasks</goal>")
        lines.append("  </overview>")
        lines.append("")
        lines.append("  <!-- Source Tasks -->")
        lines.append("  <sources>")
        for plan_file in quick_plans:
            lines.append(f"    <task file=\"{plan_file.name}\"/>")
        lines.append("  </sources>")
        lines.append("")
        lines.append(f"  <tasks>")
        lines.append(f"    <!-- {len(all_tasks)} total tasks -->")
        lines.append("")
        
        for task in all_tasks:
            indented_task = '\n'.join('    ' + line for line in task.strip().split('\n'))
            lines.append(indented_task)
            lines.append("")
        
        lines.append("  </tasks>")
        lines.append("</plan>")
        
        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Plan Merger: Merge or split GSD plans",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s merge 1-1-PLAN.md 1-2-PLAN.md --name "Auth System"
  %(prog)s split 1-1-PLAN.md --after 3,6           # Split into 3 plans
  %(prog)s consolidate-quick                       # Consolidate quick tasks
        """
    )
    
    parser.add_argument("action", choices=["merge", "split", "consolidate-quick"],
                        help="Action to perform")
    parser.add_argument("plans", nargs="*", help="Plan files to process")
    parser.add_argument("--dir", default=".", help="Project directory")
    parser.add_argument("--name", help="Name for merged plan")
    parser.add_argument("--after", help="Split points (comma-separated task numbers)")
    parser.add_argument("--output", type=Path, help="Output file")
    parser.add_argument("--preview", action="store_true", help="Preview only, don't save")
    
    args = parser.parse_args()
    
    project_path = Path(args.dir).resolve()
    planning_dir = project_path / ".planning"
    
    if not planning_dir.exists():
        print(f"❌ GSD not initialized in {project_path}")
        return 1
    
    merger = PlanMerger(planning_dir)
    
    try:
        if args.action == "merge":
            if len(args.plans) < 2:
                print("❌ Need at least 2 plans to merge")
                return 1
            
            name = args.name or f"Merged {len(args.plans)} Plans"
            result = merger.merge_plans(args.plans, name)
            
            print(f"✅ Merged {len(args.plans)} plans")
            print(f"   Output: ~{len(result.split(chr(10)))} lines")
        
        elif args.action == "split":
            if len(args.plans) != 1:
                print("❌ Need exactly 1 plan to split")
                return 1
            
            if not args.after:
                print("❌ Need --after to specify split points")
                return 1
            
            split_points = [int(x.strip()) for x in args.after.split(",")]
            results = merger.split_plan(args.plans[0], split_points)
            
            print(f"✅ Split into {len(results)} plans")
            
            for i, result in enumerate(results, 1):
                print(f"\n--- Plan {i} ---")
                print(result[:500] + "..." if len(result) > 500 else result)
            
            return 0
        
        elif args.action == "consolidate-quick":
            result = merger.consolidate_quick_tasks()
            if not result:
                print("❌ No quick tasks found")
                return 1
            
            print("✅ Consolidated quick tasks")
        
        # Output
        if args.preview:
            print("\n--- Preview ---")
            print(result)
        elif args.output:
            args.output.write_text(result)
            print(f"\n✅ Saved to: {args.output}")
        else:
            # Default output name
            if args.action == "merge":
                default_name = "MERGED-PLAN.md"
            elif args.action == "consolidate-quick":
                default_name = "QUICK-CONSOLIDATED.md"
            else:
                default_name = "OUTPUT.md"
            
            output_path = planning_dir / default_name
            output_path.write_text(result)
            print(f"\n✅ Saved to: {output_path}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
