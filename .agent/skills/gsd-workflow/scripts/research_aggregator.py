#!/usr/bin/env python3
"""
Research Aggregator: Collect and synthesize research notes into structured format.
Helps consolidate research from multiple sources before planning.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ResearchAggregator:
    """Aggregate and synthesize research notes."""
    
    RESEARCH_CATEGORIES = [
        "stack",
        "features", 
        "architecture",
        "pitfalls",
        "patterns",
        "libraries",
        "security",
        "performance"
    ]
    
    def __init__(self, planning_dir: Path):
        self.planning_dir = planning_dir
        self.research_dir = planning_dir / "research"
        self.research_dir.mkdir(exist_ok=True)
    
    def list_research_files(self, phase: Optional[int] = None) -> List[Path]:
        """List all research files."""
        files = []
        
        if self.research_dir.exists():
            # Phase-specific research
            if phase:
                pattern = f"{phase}-*-research.md"
                files.extend(sorted(self.research_dir.glob(pattern)))
            else:
                # All research files
                files.extend(sorted(self.research_dir.glob("*-*-research.md")))
                # General research
                files.extend(sorted(self.research_dir.glob("*.md")))
        
        return files
    
    def parse_research_file(self, filepath: Path) -> Dict:
        """Parse a research file and extract structured data."""
        content = filepath.read_text()
        
        research = {
            "file": filepath.name,
            "title": self._extract_title(content),
            "category": self._detect_category(filepath.name, content),
            "sources": self._extract_sources(content),
            "key_findings": self._extract_findings(content),
            "recommendations": self._extract_recommendations(content),
            "raw_content": content
        }
        
        return research
    
    def _extract_title(self, content: str) -> str:
        """Extract title from markdown."""
        match = re.search(r'^# (.+)$', content, re.MULTILINE)
        return match.group(1) if match else "Untitled"
    
    def _detect_category(self, filename: str, content: str) -> str:
        """Detect research category from filename or content."""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        for category in self.RESEARCH_CATEGORIES:
            if category in filename_lower or category in content_lower:
                return category
        
        return "general"
    
    def _extract_sources(self, content: str) -> List[str]:
        """Extract sources/references from content."""
        sources = []
        
        # Look for URLs
        urls = re.findall(r'https?://[^\s\)>\]]+', content)
        sources.extend(urls)
        
        # Look for source sections
        source_section = re.search(r'##? (?:Sources|References|Links)(.+?)(?=##|\Z)', content, re.DOTALL | re.IGNORECASE)
        if source_section:
            lines = source_section.group(1).strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and line.startswith('-'):
                    sources.append(line[1:].strip())
        
        return sources
    
    def _extract_findings(self, content: str) -> List[str]:
        """Extract key findings from content."""
        findings = []
        
        # Look for findings section
        findings_match = re.search(r'##? (?:Key Findings|Findings|Key Points)(.+?)(?=##|\Z)', content, re.DOTALL | re.IGNORECASE)
        if findings_match:
            section = findings_match.group(1)
            # Extract bullet points
            bullets = re.findall(r'^[\s]*[-*][\s]+(.+)$', section, re.MULTILINE)
            findings.extend(bullets)
        
        return findings
    
    def _extract_recommendations(self, content: str) -> List[str]:
        """Extract recommendations from content."""
        recommendations = []
        
        # Look for recommendations section
        rec_match = re.search(r'##? (?:Recommendations|Recommendation|Suggested)(.+?)(?=##|\Z)', content, re.DOTALL | re.IGNORECASE)
        if rec_match:
            section = rec_match.group(1)
            bullets = re.findall(r'^[\s]*[-*][\s]+(.+)$', section, re.MULTILINE)
            recommendations.extend(bullets)
        
        return recommendations
    
    def aggregate(self, phase: Optional[int] = None) -> Dict:
        """Aggregate all research into structured format."""
        files = self.list_research_files(phase)
        
        if not files:
            return {"error": "No research files found"}
        
        aggregated = {
            "phase": phase,
            "files_processed": len(files),
            "by_category": {cat: [] for cat in self.RESEARCH_CATEGORIES},
            "all_findings": [],
            "all_recommendations": [],
            "all_sources": [],
            "files": []
        }
        
        for filepath in files:
            research = self.parse_research_file(filepath)
            aggregated["files"].append(research)
            
            # Categorize
            category = research["category"]
            if category in aggregated["by_category"]:
                aggregated["by_category"][category].append(research)
            
            # Collect findings
            aggregated["all_findings"].extend(research["key_findings"])
            
            # Collect recommendations
            aggregated["all_recommendations"].extend(research["recommendations"])
            
            # Collect sources
            aggregated["all_sources"].extend(research["sources"])
        
        # Remove duplicates from sources
        aggregated["all_sources"] = list(dict.fromkeys(aggregated["all_sources"]))
        
        return aggregated
    
    def generate_report(self, phase: Optional[int] = None, output: Optional[Path] = None) -> str:
        """Generate aggregated research report."""
        data = self.aggregate(phase)
        
        if "error" in data:
            return f"❌ {data['error']}"
        
        lines = []
        
        lines.append(f"# Research Summary")
        if phase:
            lines.append(f"\n**Phase**: {phase}")
        lines.append(f"**Files Processed**: {data['files_processed']}")
        lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Summary by category
        lines.append("## Research by Category")
        lines.append("")
        
        for category, researches in data["by_category"].items():
            if researches:
                lines.append(f"### {category.title()}")
                lines.append("")
                for r in researches:
                    lines.append(f"- **{r['title']}** ({r['file']})")
                    if r['key_findings']:
                        lines.append(f"  - {len(r['key_findings'])} findings")
                lines.append("")
        
        # Key Findings
        if data["all_findings"]:
            lines.append("## Key Findings")
            lines.append("")
            for i, finding in enumerate(data["all_findings"][:20], 1):  # Limit to 20
                lines.append(f"{i}. {finding}")
            if len(data["all_findings"]) > 20:
                lines.append(f"\n... and {len(data['all_findings']) - 20} more")
            lines.append("")
        
        # Recommendations
        if data["all_recommendations"]:
            lines.append("## Recommendations")
            lines.append("")
            for i, rec in enumerate(data["all_recommendations"], 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
        
        # Sources
        if data["all_sources"]:
            lines.append("## Sources & References")
            lines.append("")
            for source in data["all_sources"][:30]:  # Limit to 30
                lines.append(f"- {source}")
            if len(data["all_sources"]) > 30:
                lines.append(f"\n... and {len(data['all_sources']) - 30} more")
            lines.append("")
        
        # Individual research summaries
        lines.append("## Research Details")
        lines.append("")
        
        for research in data["files"]:
            lines.append(f"### {research['title']}")
            lines.append(f"*File: `{research['file']}`*")
            lines.append("")
            
            if research['key_findings']:
                lines.append("**Key Findings:**")
                for finding in research['key_findings'][:5]:  # Top 5
                    lines.append(f"- {finding}")
                lines.append("")
            
            if research['recommendations']:
                lines.append("**Recommendations:**")
                for rec in research['recommendations'][:3]:  # Top 3
                    lines.append(f"- {rec}")
                lines.append("")
        
        report = "\n".join(lines)
        
        # Save if output specified
        if output:
            output.write_text(report)
            print(f"✅ Report saved to: {output}")
        
        return report
    
    def generate_planning_input(self, phase: int, output: Optional[Path] = None) -> str:
        """Generate concise input for planning phase."""
        data = self.aggregate(phase)
        
        if "error" in data:
            return f"❌ {data['error']}"
        
        lines = []
        lines.append(f"# Research Input for Phase {phase} Planning")
        lines.append("")
        lines.append("## Key Decisions")
        lines.append("")
        
        # Extract recommendations as decisions
        for rec in data["all_recommendations"][:10]:
            lines.append(f"- {rec}")
        
        lines.append("")
        lines.append("## Technical Insights")
        lines.append("")
        
        # Stack insights
        stack_research = data["by_category"].get("stack", [])
        if stack_research:
            for r in stack_research:
                for finding in r["key_findings"][:3]:
                    lines.append(f"- **Stack**: {finding}")
        
        # Architecture insights
        arch_research = data["by_category"].get("architecture", [])
        if arch_research:
            for r in arch_research:
                for finding in r["key_findings"][:3]:
                    lines.append(f"- **Architecture**: {finding}")
        
        # Pitfalls to avoid
        pitfalls = data["by_category"].get("pitfalls", [])
        if pitfalls:
            lines.append("")
            lines.append("## Pitfalls to Avoid")
            lines.append("")
            for r in pitfalls:
                for finding in r["key_findings"][:5]:
                    lines.append(f"- ⚠️ {finding}")
        
        content = "\n".join(lines)
        
        if output:
            output.write_text(content)
            print(f"✅ Planning input saved to: {output}")
        
        return content


def main():
    parser = argparse.ArgumentParser(
        description="Research Aggregator: Collect and synthesize research notes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Aggregate all research
  %(prog)s --phase 1                 # Aggregate phase 1 research
  %(prog)s --phase 2 --output research-summary.md
  %(prog)s --phase 3 --planning-input  # Generate planning input
        """
    )
    
    parser.add_argument("--dir", default=".", help="Project directory")
    parser.add_argument("--phase", type=int, help="Phase number to aggregate")
    parser.add_argument("--output", type=Path, help="Output file for full report")
    parser.add_argument("--planning-input", action="store_true", 
                        help="Generate concise input for planning")
    parser.add_argument("--list", action="store_true", 
                        help="List available research files")
    
    args = parser.parse_args()
    
    project_path = Path(args.dir).resolve()
    planning_dir = project_path / ".planning"
    
    if not planning_dir.exists():
        print(f"❌ GSD not initialized in {project_path}")
        return 1
    
    aggregator = ResearchAggregator(planning_dir)
    
    if args.list:
        files = aggregator.list_research_files(args.phase)
        print(f"\n📚 Research Files ({len(files)} total):")
        print("-" * 40)
        for f in files:
            research = aggregator.parse_research_file(f)
            print(f"  • {f.name}")
            print(f"    Title: {research['title']}")
            print(f"    Category: {research['category']}")
            print()
        return 0
    
    if args.planning_input:
        output = args.output or (planning_dir / f"{args.phase}-RESEARCH-INPUT.md" if args.phase else None)
        content = aggregator.generate_planning_input(args.phase, output)
        print(content)
    else:
        output = args.output or (planning_dir / f"{args.phase}-RESEARCH-SUMMARY.md" if args.phase else None)
        report = aggregator.generate_report(args.phase, output)
        print(report)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
