#!/usr/bin/env python3
"""
Wave Planner: Analyze plan dependencies and create parallel execution schedule.
GSD plans execute in "waves" - independent plans in parallel, dependent plans sequential.
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


class PlanAnalyzer:
    """Analyze plan files for dependencies and execution order."""
    
    def __init__(self, planning_dir: Path):
        self.planning_dir = planning_dir
        self.plans: Dict[str, dict] = {}
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.dependents: Dict[str, Set[str]] = defaultdict(set)
    
    def load_plans(self, phase: int) -> None:
        """Load all plan files for a phase."""
        pattern = f"{phase}-*-PLAN.md"
        plan_files = sorted(self.planning_dir.glob(pattern))
        
        for plan_file in plan_files:
            plan_id = self._extract_plan_id(plan_file.name)
            content = plan_file.read_text()
            
            self.plans[plan_id] = {
                "file": plan_file.name,
                "path": plan_file,
                "content": content,
                "tasks": self._count_tasks(content),
                "dependencies": self._extract_dependencies(content),
            }
            
            # Build dependency graph
            for dep in self.plans[plan_id]["dependencies"]:
                self.dependencies[plan_id].add(dep)
                self.dependents[dep].add(plan_id)
    
    def _extract_plan_id(self, filename: str) -> str:
        """Extract plan ID from filename (e.g., '1-1-PLAN.md' -> '1-1')."""
        match = re.match(r'(\d+-\d+)', filename)
        return match.group(1) if match else filename
    
    def _count_tasks(self, content: str) -> int:
        """Count number of tasks in a plan."""
        return len(re.findall(r'<task\s+', content))
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from plan content."""
        deps = []
        
        # Look for dependencies section
        deps_match = re.search(r'<dependencies>(.*?)</dependencies>', content, re.DOTALL)
        if deps_match:
            deps_section = deps_match.group(1)
            # Find complete dependencies
            complete_deps = re.findall(r'<complete>(.*?)</complete>', deps_section)
            for dep in complete_deps:
                # Try to extract plan reference (e.g., "Plan 1", "Phase 1 Plan 1")
                plan_match = re.search(r'[Pp]lan\s+(\d+)', dep)
                phase_match = re.search(r'[Pp]hase\s+(\d+)', dep)
                
                if plan_match:
                    plan_num = plan_match.group(1)
                    if phase_match:
                        phase_num = phase_match.group(1)
                        deps.append(f"{phase_num}-{plan_num}")
                    else:
                        # Assume same phase
                        current_phase = self._extract_phase_from_content(content)
                        if current_phase:
                            deps.append(f"{current_phase}-{plan_num}")
        
        return deps
    
    def _extract_phase_from_content(self, content: str) -> str:
        """Extract phase number from plan content."""
        match = re.search(r'<plan\s+phase="(\d+)"', content)
        return match.group(1) if match else None
    
    def detect_cycles(self) -> List[List[str]]:
        """Detect circular dependencies."""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.dependencies[node]:
                if neighbor not in visited:
                    dfs(neighbor, path)
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
            
            path.pop()
            rec_stack.remove(node)
        
        for plan_id in self.plans:
            if plan_id not in visited:
                dfs(plan_id, [])
        
        return cycles
    
    def calculate_waves(self) -> List[List[str]]:
        """Calculate execution waves using topological sort."""
        # Kahn's algorithm
        in_degree = {plan_id: len(self.dependencies[plan_id]) for plan_id in self.plans}
        
        waves = []
        remaining = set(self.plans.keys())
        
        while remaining:
            # Find all plans with no remaining dependencies
            wave = [plan_id for plan_id in remaining if in_degree[plan_id] == 0]
            
            if not wave:
                # Circular dependency detected
                break
            
            waves.append(sorted(wave))
            
            # Remove this wave from consideration
            for plan_id in wave:
                remaining.remove(plan_id)
                # Reduce in-degree for dependents
                for dependent in self.dependents[plan_id]:
                    if dependent in in_degree:
                        in_degree[dependent] -= 1
        
        # Handle remaining plans (circular deps)
        if remaining:
            waves.append(sorted(remaining))
        
        return waves
    
    def estimate_duration(self, plan_id: str) -> int:
        """Estimate plan duration in minutes based on task count."""
        task_count = self.plans[plan_id]["tasks"]
        # Rough estimate: 5-15 mins per task
        return task_count * 10
    
    def generate_report(self, phase: int) -> str:
        """Generate execution schedule report."""
        lines = []
        
        lines.append(f"\n{'='*60}")
        lines.append(f"🌊 WAVE EXECUTION PLAN - Phase {phase}")
        lines.append(f"{'='*60}\n")
        
        # Plans summary
        lines.append(f"📋 PLANS ({len(self.plans)} total)")
        lines.append("-" * 40)
        
        for plan_id in sorted(self.plans.keys()):
            plan = self.plans[plan_id]
            deps_str = f" (depends on: {', '.join(plan['dependencies'])})" if plan['dependencies'] else ""
            lines.append(f"  • {plan_id}: {plan['tasks']} tasks{deps_str}")
        
        lines.append("")
        
        # Check for cycles
        cycles = self.detect_cycles()
        if cycles:
            lines.append("⚠️  CIRCULAR DEPENDENCIES DETECTED!")
            for cycle in cycles:
                lines.append(f"   {' → '.join(cycle)}")
            lines.append("")
        
        # Calculate waves
        waves = self.calculate_waves()
        
        lines.append(f"🌊 EXECUTION WAVES ({len(waves)} total)")
        lines.append("-" * 40)
        
        total_estimated_time = 0
        
        for i, wave in enumerate(waves, 1):
            lines.append(f"\n  WAVE {i} (parallel):")
            
            wave_duration = 0
            for plan_id in wave:
                plan = self.plans.get(plan_id, {})
                duration = self.estimate_duration(plan_id)
                wave_duration = max(wave_duration, duration)
                
                task_info = f"{plan.get('tasks', 0)} tasks"
                time_info = f"~{duration} min"
                
                # Mark if this was part of a cycle
                marker = " 🔁" if any(plan_id in cycle for cycle in cycles) else ""
                
                lines.append(f"    • {plan_id}: {task_info}, {time_info}{marker}")
            
            total_estimated_time += wave_duration
            lines.append(f"    └─ Wave duration: ~{wave_duration} min")
        
        lines.append(f"\n  ⏱️  Total estimated time: ~{total_estimated_time} minutes")
        lines.append("")
        
        # Execution strategy
        lines.append("📊 EXECUTION STRATEGY")
        lines.append("-" * 40)
        
        parallelizable = sum(len(wave) for wave in waves if len(wave) > 1)
        sequential = sum(1 for wave in waves if len(wave) == 1)
        
        lines.append(f"  • Parallelizable plans: {parallelizable}")
        lines.append(f"  • Sequential waves: {len(waves)}")
        lines.append(f"  • Parallelization efficiency: {parallelizable/max(1, len(self.plans))*100:.0f}%")
        
        if parallelizable == 0:
            lines.append("\n  💡 Tip: All plans are sequential. Consider breaking")
            lines.append("     dependencies or reorganizing into vertical slices.")
        elif len(waves) == 1:
            lines.append("\n  ✅ All plans can run in parallel!")
        
        lines.append(f"\n{'='*60}\n")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Wave Planner: Analyze plan dependencies and create execution schedule",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 1                    # Analyze phase 1 plans
  %(prog)s 2 --dir ./my-project # Analyze phase 2 in specific directory
        """
    )
    
    parser.add_argument("phase", type=int, help="Phase number to analyze")
    parser.add_argument("--dir", default=".", help="Project directory (default: current)")
    
    args = parser.parse_args()
    
    project_path = Path(args.dir).resolve()
    planning_dir = project_path / ".planning"
    
    if not planning_dir.exists():
        print(f"❌ GSD not initialized in {project_path}")
        return 1
    
    # Load and analyze plans
    analyzer = PlanAnalyzer(planning_dir)
    analyzer.load_plans(args.phase)
    
    if not analyzer.plans:
        print(f"❌ No plans found for phase {args.phase}")
        print(f"   Looking for: {args.phase}-*-PLAN.md")
        return 1
    
    # Generate and print report
    report = analyzer.generate_report(args.phase)
    print(report)
    
    # Exit with error if cycles detected
    cycles = analyzer.detect_cycles()
    return 1 if cycles else 0


if __name__ == "__main__":
    sys.exit(main())
