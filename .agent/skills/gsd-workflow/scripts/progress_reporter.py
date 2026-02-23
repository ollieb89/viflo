#!/usr/bin/env python3
"""
Progress Reporter: Generate detailed progress reports in markdown format.
Useful for standups, stakeholder updates, or project retrospectives.
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ProgressReporter:
    """Generate progress reports from GSD artifacts."""
    
    def __init__(self, planning_dir: Path):
        self.planning_dir = planning_dir
        self.project_file = planning_dir / "PROJECT.md"
        self.roadmap_file = planning_dir / "ROADMAP.md"
        self.state_file = planning_dir / "STATE.md"
    
    def get_project_info(self) -> Dict:
        """Extract project info from PROJECT.md."""
        if not self.project_file.exists():
            return {"name": "Unknown Project", "vision": ""}
        
        content = self.project_file.read_text()
        
        # Extract title
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        name = title_match.group(1) if title_match else "Unknown Project"
        
        # Extract vision
        vision_match = re.search(r'## Vision\s*\n\s*([^\n]+)', content)
        vision = vision_match.group(1) if vision_match else ""
        
        return {"name": name, "vision": vision}
    
    def get_phase_data(self) -> List[Dict]:
        """Extract phase data from ROADMAP.md and plan files."""
        if not self.roadmap_file.exists():
            return []
        
        content = self.roadmap_file.read_text()
        phases = []
        
        # Parse each phase section
        phase_pattern = r'## Phase (\d+):([^\n]+)\n([^#]+)'
        for match in re.finditer(phase_pattern, content, re.DOTALL):
            phase_num = int(match.group(1))
            phase_name = match.group(2).strip()
            section = match.group(3)
            
            # Extract status
            status_match = re.search(r'\*\*Status\*\*:\s*(\w+)', section)
            status = status_match.group(1).lower() if status_match else "unknown"
            
            # Extract requirements
            reqs_match = re.search(r'\*\*Requirements\*\*:\s*([^\n]+)', section)
            requirements = reqs_match.group(1).strip() if reqs_match else ""
            
            # Count plans and completion
            plans = list(self.planning_dir.glob(f"{phase_num}-*-PLAN.md"))
            summaries = list(self.planning_dir.glob(f"{phase_num}-*-SUMMARY.md"))
            
            phases.append({
                "num": phase_num,
                "name": phase_name,
                "status": status,
                "requirements": requirements,
                "plans_total": len(plans),
                "plans_completed": len(summaries),
                "progress_pct": (len(summaries) / len(plans) * 100) if plans else 0
            })
        
        return sorted(phases, key=lambda x: x["num"])
    
    def get_recent_activity(self, days: int = 7) -> List[Dict]:
        """Get recent activity from summary files and STATE.md."""
        activity = []
        
        # Check summary files
        for summary_file in sorted(self.planning_dir.glob("*-*-SUMMARY.md")):
            stat = summary_file.stat()
            file_time = datetime.fromtimestamp(stat.st_mtime)
            
            # Read first few lines for title
            content = summary_file.read_text()
            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else summary_file.name
            
            activity.append({
                "type": "completion",
                "title": title,
                "file": summary_file.name,
                "date": file_time,
                "phase": self._extract_phase_from_file(summary_file.name)
            })
        
        # Sort by date
        return sorted(activity, key=lambda x: x["date"], reverse=True)[:10]
    
    def _extract_phase_from_file(self, filename: str) -> int:
        """Extract phase number from filename."""
        match = re.match(r'(\d+)-', filename)
        return int(match.group(1)) if match else 0
    
    def get_blockers(self) -> List[str]:
        """Extract blockers from STATE.md."""
        if not self.state_file.exists():
            return []
        
        content = self.state_file.read_text()
        
        blockers = []
        blockers_section = re.search(r'## Blockers\s*\n([^#]+)', content)
        if blockers_section:
            lines = blockers_section.group(1).strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('- [ ]'):
                    blockers.append(line[5:].strip())
        
        return blockers
    
    def get_upcoming_work(self) -> List[Dict]:
        """Get upcoming work from plans."""
        upcoming = []
        
        for plan_file in sorted(self.planning_dir.glob("*-*-PLAN.md")):
            # Check if summary exists
            summary_file = plan_file.with_name(plan_file.name.replace("-PLAN.md", "-SUMMARY.md"))
            if summary_file.exists():
                continue  # Already completed
            
            content = plan_file.read_text()
            phase = self._extract_phase_from_file(plan_file.name)
            
            # Extract overview
            overview_match = re.search(r'<phase_name>([^<]+)</phase_name>', content)
            name = overview_match.group(1).strip() if overview_match else plan_file.name
            
            # Count tasks
            task_count = len(re.findall(r'<task\s+', content))
            
            upcoming.append({
                "phase": phase,
                "name": name,
                "file": plan_file.name,
                "tasks": task_count
            })
        
        return sorted(upcoming, key=lambda x: (x["phase"], x["file"]))[:5]
    
    def generate_report(self, format: str = "markdown") -> str:
        """Generate progress report."""
        if format == "markdown":
            return self._generate_markdown_report()
        elif format == "json":
            import json
            return json.dumps(self._generate_data(), indent=2)
        else:
            return self._generate_text_report()
    
    def _generate_data(self) -> Dict:
        """Generate report data structure."""
        return {
            "project": self.get_project_info(),
            "generated_at": datetime.now().isoformat(),
            "phases": self.get_phase_data(),
            "recent_activity": [
                {**a, "date": a["date"].isoformat()} for a in self.get_recent_activity()
            ],
            "blockers": self.get_blockers(),
            "upcoming_work": self.get_upcoming_work()
        }
    
    def _generate_markdown_report(self) -> str:
        """Generate markdown progress report."""
        lines = []
        project = self.get_project_info()
        phases = self.get_phase_data()
        activity = self.get_recent_activity()
        blockers = self.get_blockers()
        upcoming = self.get_upcoming_work()
        
        # Header
        lines.append(f"# Progress Report: {project['name']}")
        lines.append("")
        lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        if project['vision']:
            lines.append(f"**Vision**: {project['vision']}")
        lines.append("")
        
        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        
        if phases:
            complete = sum(1 for p in phases if p['status'] == 'complete')
            total = len(phases)
            overall_pct = sum(p['progress_pct'] for p in phases) / len(phases)
            
            lines.append(f"- **Overall Progress**: {overall_pct:.0f}%")
            lines.append(f"- **Phases Complete**: {complete}/{total}")
            lines.append(f"- **Current Phase**: Phase {next((p['num'] for p in phases if p['status'] != 'complete'), 'N/A')}")
        
        if blockers:
            lines.append(f"- **Active Blockers**: {len(blockers)}")
        
        lines.append("")
        
        # Phase Breakdown
        if phases:
            lines.append("## Phase Breakdown")
            lines.append("")
            lines.append("| Phase | Name | Status | Progress | Plans |")
            lines.append("|-------|------|--------|----------|-------|")
            
            for phase in phases:
                status_icon = {
                    "complete": "✅",
                    "in-progress": "🔄",
                    "planning": "📝",
                    "discussing": "💬",
                    "not-started": "⏳"
                }.get(phase['status'], "❓")
                
                progress_bar = self._progress_bar(phase['progress_pct'])
                plans = f"{phase['plans_completed']}/{phase['plans_total']}"
                
                lines.append(f"| {phase['num']} | {phase['name']} | {status_icon} {phase['status']} | {progress_bar} | {plans} |")
            
            lines.append("")
        
        # Progress Visualization
        if phases:
            lines.append("## Progress Overview")
            lines.append("")
            lines.append("```")
            for phase in phases:
                bar = self._ascii_bar(phase['progress_pct'], width=30)
                status_char = "✓" if phase['status'] == 'complete' else "○"
                lines.append(f"{status_char} Phase {phase['num']}: [{bar}] {phase['progress_pct']:.0f}%")
            lines.append("```")
            lines.append("")
        
        # Recent Activity
        if activity:
            lines.append("## Recent Activity")
            lines.append("")
            for item in activity[:5]:
                date_str = item['date'].strftime('%Y-%m-%d')
                icon = "✅" if item['type'] == 'completion' else "📝"
                lines.append(f"- {icon} **{date_str}**: {item['title']} (Phase {item['phase']})")
            lines.append("")
        
        # Blockers
        if blockers:
            lines.append("## ⚠️ Active Blockers")
            lines.append("")
            for blocker in blockers:
                lines.append(f"- [ ] {blocker}")
            lines.append("")
        
        # Upcoming Work
        if upcoming:
            lines.append("## Upcoming Work")
            lines.append("")
            for item in upcoming:
                lines.append(f"- **Phase {item['phase']}**: {item['name']} ({item['tasks']} tasks)")
            lines.append("")
        
        # Next Steps
        lines.append("## Next Steps")
        lines.append("")
        
        current_phase = next((p for p in phases if p['status'] != 'complete'), None)
        if current_phase:
            if current_phase['status'] == 'not-started':
                lines.append(f"1. Begin Phase {current_phase['num']}: Start discussion phase")
            elif current_phase['status'] == 'discussing':
                lines.append(f"1. Complete Phase {current_phase['num']}: Create plans")
            elif current_phase['status'] == 'planning':
                lines.append(f"1. Execute Phase {current_phase['num']}: {current_phase['plans_total'] - current_phase['plans_completed']} plans remaining")
            elif current_phase['status'] == 'executing':
                lines.append(f"1. Complete Phase {current_phase['num']}: Verification")
        else:
            lines.append("✅ All phases complete! Consider starting a new milestone.")
        
        if blockers:
            lines.append(f"2. Resolve {len(blockers)} active blocker(s)")
        
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_text_report(self) -> str:
        """Generate plain text report."""
        lines = []
        project = self.get_project_info()
        phases = self.get_phase_data()
        
        lines.append(f"PROGRESS REPORT: {project['name']}")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")
        
        for phase in phases:
            status_icon = "[✓]" if phase['status'] == 'complete' else "[ ]"
            lines.append(f"{status_icon} Phase {phase['num']}: {phase['name']}")
            lines.append(f"    Status: {phase['status']}")
            lines.append(f"    Progress: {phase['plans_completed']}/{phase['plans_total']} plans")
            lines.append("")
        
        return "\n".join(lines)
    
    def _progress_bar(self, pct: float, width: int = 10) -> str:
        """Generate markdown progress bar."""
        filled = int(pct / 100 * width)
        empty = width - filled
        return "█" * filled + "░" * empty + f" {pct:.0f}%"
    
    def _ascii_bar(self, pct: float, width: int = 30) -> str:
        """Generate ASCII progress bar."""
        filled = int(pct / 100 * width)
        empty = width - filled
        return "=" * filled + "-" * empty


def main():
    parser = argparse.ArgumentParser(
        description="Progress Reporter: Generate detailed progress reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Generate markdown report
  %(prog)s --format json             # Generate JSON report
  %(prog)s --output progress.md      # Save to file
  %(prog)s --days 14                 # Include 14 days of activity
        """
    )
    
    parser.add_argument("--dir", default=".", help="Project directory")
    parser.add_argument("--format", choices=["markdown", "json", "text"], 
                        default="markdown", help="Output format")
    parser.add_argument("--output", type=Path, help="Output file")
    parser.add_argument("--days", type=int, default=7, help="Days of activity to include")
    
    args = parser.parse_args()
    
    project_path = Path(args.dir).resolve()
    planning_dir = project_path / ".planning"
    
    if not planning_dir.exists():
        print(f"❌ GSD not initialized in {project_path}")
        return 1
    
    reporter = ProgressReporter(planning_dir)
    report = reporter.generate_report(args.format)
    
    if args.output:
        args.output.write_text(report)
        print(f"✅ Report saved to: {args.output}")
    else:
        print(report)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
