#!/usr/bin/env python3
"""
Dependency Visualizer: Create visual/text representations of plan dependencies.
Outputs Mermaid diagrams, ASCII trees, or DOT format for graphviz.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class DependencyVisualizer:
    """Visualize plan dependencies."""
    
    def __init__(self, planning_dir: Path):
        self.planning_dir = planning_dir
        self.graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)
        self.plan_info: Dict[str, Dict] = {}
    
    def load_phase(self, phase: int) -> None:
        """Load all plans for a phase."""
        for plan_file in sorted(self.planning_dir.glob(f"{phase}-*-PLAN.md")):
            plan_id = self._extract_plan_id(plan_file.name)
            content = plan_file.read_text()
            
            # Extract info
            info = {
                "file": plan_file.name,
                "name": self._extract_name(content),
                "tasks": len(re.findall(r'<task\s+', content)),
                "dependencies": self._extract_dependencies(content),
            }
            
            self.plan_info[plan_id] = info
            
            # Build graph
            for dep in info["dependencies"]:
                self.graph[plan_id].add(dep)
                self.reverse_graph[dep].add(plan_id)
    
    def _extract_plan_id(self, filename: str) -> str:
        """Extract plan ID from filename."""
        match = re.match(r'(\d+-\d+)', filename)
        return match.group(1) if match else filename
    
    def _extract_name(self, content: str) -> str:
        """Extract plan name from content."""
        match = re.search(r'<phase_name>([^<]+)</phase_name>', content)
        return match.group(1).strip() if match else "Unknown"
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from plan content."""
        deps = []
        deps_match = re.search(r'<dependencies>(.+?)</dependencies>', content, re.DOTALL)
        
        if deps_match:
            # Look for plan references
            refs = re.findall(r'[Pp]lan\s+(\d+)', deps_match.group(1))
            current_phase = self._extract_phase_from_content(content)
            
            for ref in refs:
                if current_phase:
                    deps.append(f"{current_phase}-{ref}")
        
        return deps
    
    def _extract_phase_from_content(self, content: str) -> str:
        """Extract phase from plan tag."""
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
            
            for neighbor in self.graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path)
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
            
            path.pop()
            rec_stack.remove(node)
        
        for node in self.plan_info:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def to_mermaid(self) -> str:
        """Generate Mermaid flowchart."""
        lines = ["```mermaid", "flowchart TD"]
        
        # Add nodes
        for plan_id, info in sorted(self.plan_info.items()):
            short_name = info["name"][:20] + "..." if len(info["name"]) > 20 else info["name"]
            safe_name = re.sub(r'[^\w\s]', '', short_name)
            lines.append(f'    {plan_id}["{plan_id}<br/>{safe_name}"]')
        
        lines.append("")
        
        # Add edges
        for plan_id, deps in sorted(self.graph.items()):
            for dep in sorted(deps):
                lines.append(f"    {dep} --> {plan_id}")
        
        # Style cycles
        cycles = self.detect_cycles()
        if cycles:
            lines.append("")
            lines.append("    %% Cycles detected")
            cycle_nodes = set()
            for cycle in cycles:
                cycle_nodes.update(cycle[:-1])  # Exclude repeated node
            
            for node in cycle_nodes:
                lines.append(f"    style {node} fill:#f9f,stroke:#333,stroke-width:2px")
        
        lines.append("```")
        
        return "\n".join(lines)
    
    def to_ascii_tree(self) -> str:
        """Generate ASCII tree representation."""
        lines = []
        lines.append("Plan Dependency Tree")
        lines.append("=" * 60)
        lines.append("")
        
        # Find root nodes (no dependencies)
        roots = [pid for pid in self.plan_info if not self.graph.get(pid)]
        
        if not roots:
            lines.append("No root plans found (all plans have dependencies)")
            if self.plan_info:
                lines.append("Possible circular dependencies!")
            return "\n".join(lines)
        
        for root in sorted(roots):
            self._print_tree_node(root, "", lines, set())
        
        # Check for disconnected nodes
        connected = set(roots)
        for pid in self.plan_info:
            connected.update(self.reverse_graph.get(pid, []))
        
        disconnected = set(self.plan_info.keys()) - connected
        if disconnected:
            lines.append("")
            lines.append("Disconnected Plans (no dependencies, not depended on):")
            for pid in sorted(disconnected):
                info = self.plan_info[pid]
                lines.append(f"  • {pid}: {info['name']}")
        
        return "\n".join(lines)
    
    def _print_tree_node(self, node: str, prefix: str, lines: List[str], visited: Set[str]):
        """Recursively print tree node."""
        if node in visited:
            lines.append(f"{prefix}└── {node} [CIRCULAR]")
            return
        
        visited.add(node)
        info = self.plan_info.get(node, {})
        name = info.get("name", "Unknown")
        
        lines.append(f"{prefix}{node}: {name[:30]}")
        
        # Print children (plans that depend on this)
        children = sorted(self.reverse_graph.get(node, []))
        for i, child in enumerate(children):
            is_last = (i == len(children) - 1)
            new_prefix = prefix + ("    " if is_last else "│   ")
            connector = "└── " if is_last else "├── "
            
            if child in visited:
                lines.append(f"{prefix}{connector}{child} [...]")
            else:
                self._print_tree_node(child, new_prefix, lines, visited.copy())
    
    def to_dot(self) -> str:
        """Generate Graphviz DOT format."""
        lines = ["digraph PlanDependencies {"]
        lines.append("    rankdir=TB;")
        lines.append("    node [shape=box, style=rounded];")
        lines.append("")
        
        # Add nodes
        for plan_id, info in sorted(self.plan_info.items()):
            short_name = info["name"][:25] + "..." if len(info["name"]) > 25 else info["name"]
            safe_name = re.sub(r'["]', r'\\"', short_name)
            lines.append(f'    "{plan_id}" [label="{plan_id}\\n{safe_name}"];')
        
        lines.append("")
        
        # Add edges
        for plan_id, deps in sorted(self.graph.items()):
            for dep in sorted(deps):
                lines.append(f'    "{dep}" -> "{plan_id}";')
        
        # Highlight cycles
        cycles = self.detect_cycles()
        if cycles:
            lines.append("")
            lines.append("    // Cycles")
            cycle_nodes = set()
            for cycle in cycles:
                cycle_nodes.update(cycle[:-1])
            
            for node in sorted(cycle_nodes):
                lines.append(f'    "{node}" [style=filled, fillcolor="#ffcccc"];')
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def to_table(self) -> str:
        """Generate markdown table of dependencies."""
        lines = []
        lines.append("| Plan | Name | Dependencies | Dependents |")
        lines.append("|------|------|--------------|------------|")
        
        for plan_id in sorted(self.plan_info.keys()):
            info = self.plan_info[plan_id]
            deps = ", ".join(sorted(self.graph.get(plan_id, []))) or "None"
            dependents = ", ".join(sorted(self.reverse_graph.get(plan_id, []))) or "None"
            name = info["name"][:30] + "..." if len(info["name"]) > 30 else info["name"]
            
            lines.append(f"| {plan_id} | {name} | {deps} | {dependents} |")
        
        return "\n".join(lines)
    
    def analyze(self) -> str:
        """Generate dependency analysis report."""
        lines = []
        lines.append("# Dependency Analysis")
        lines.append("")
        
        # Summary
        total = len(self.plan_info)
        independent = sum(1 for pid in self.plan_info if not self.graph.get(pid))
        has_deps = total - independent
        
        lines.append(f"**Total Plans**: {total}")
        lines.append(f"**Independent**: {independent} (can start immediately)")
        lines.append(f"**Has Dependencies**: {has_deps}")
        lines.append("")
        
        # Critical path analysis
        lines.append("## Critical Path Analysis")
        lines.append("")
        
        # Find longest dependency chain
        max_depth = 0
        deepest = []
        
        for pid in self.plan_info:
            depth = self._calc_depth(pid, {})
            if depth > max_depth:
                max_depth = depth
                deepest = [pid]
            elif depth == max_depth:
                deepest.append(pid)
        
        lines.append(f"**Maximum Dependency Depth**: {max_depth} levels")
        lines.append(f"**Deepest Plans**: {', '.join(deepest)}")
        lines.append("")
        
        # Bottlenecks (plans many others depend on)
        lines.append("## Bottleneck Plans")
        lines.append("")
        lines.append("Plans that many others depend on (finish these first!):")
        lines.append("")
        
        bottlenecks = [(pid, len(self.reverse_graph.get(pid, []))) for pid in self.plan_info]
        bottlenecks.sort(key=lambda x: x[1], reverse=True)
        
        for pid, count in bottlenecks[:5]:
            if count > 0:
                info = self.plan_info[pid]
                lines.append(f"- **{pid}** ({info['name']}): {count} plans depend on this")
        
        if all(count == 0 for _, count in bottlenecks):
            lines.append("No bottlenecks - plans are independent!")
        
        lines.append("")
        
        # Cycles
        cycles = self.detect_cycles()
        if cycles:
            lines.append("## ⚠️ Circular Dependencies Detected")
            lines.append("")
            for i, cycle in enumerate(cycles, 1):
                lines.append(f"{i}. {' → '.join(cycle)}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _calc_depth(self, node: str, memo: Dict[str, int]) -> int:
        """Calculate dependency depth for a node."""
        if node in memo:
            return memo[node]
        
        deps = self.graph.get(node, [])
        if not deps:
            memo[node] = 1
            return 1
        
        depth = 1 + max(self._calc_depth(dep, memo) for dep in deps)
        memo[node] = depth
        return depth


def main():
    parser = argparse.ArgumentParser(
        description="Dependency Visualizer: Visualize plan dependencies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 1                         # ASCII tree for phase 1
  %(prog)s 2 --format mermaid        # Mermaid diagram
  %(prog)s 1 --format dot            # Graphviz DOT format
  %(prog)s 3 --format table          # Markdown table
  %(prog)s 1 --analyze               # Dependency analysis
        """
    )
    
    parser.add_argument("phase", type=int, help="Phase number to visualize")
    parser.add_argument("--dir", default=".", help="Project directory")
    parser.add_argument("--format", choices=["ascii", "mermaid", "dot", "table"],
                        default="ascii", help="Output format")
    parser.add_argument("--analyze", action="store_true", help="Show analysis report")
    parser.add_argument("--output", type=Path, help="Output file")
    
    args = parser.parse_args()
    
    project_path = Path(args.dir).resolve()
    planning_dir = project_path / ".planning"
    
    if not planning_dir.exists():
        print(f"❌ GSD not initialized in {project_path}")
        return 1
    
    visualizer = DependencyVisualizer(planning_dir)
    visualizer.load_phase(args.phase)
    
    if not visualizer.plan_info:
        print(f"❌ No plans found for phase {args.phase}")
        return 1
    
    # Generate output
    if args.analyze:
        output = visualizer.analyze()
    else:
        formatters = {
            "ascii": visualizer.to_ascii_tree,
            "mermaid": visualizer.to_mermaid,
            "dot": visualizer.to_dot,
            "table": visualizer.to_table,
        }
        output = formatters[args.format]()
    
    # Output
    if args.output:
        args.output.write_text(output)
        print(f"✅ Output saved to: {args.output}")
    else:
        print(output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
