#!/usr/bin/env python3
"""
Project Generator: Interactive generator for PROJECT.md from user input.
Asks questions and generates a complete project specification.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ProjectGenerator:
    """Generate PROJECT.md from interactive input."""
    
    # Common tech stack options
    FRONTEND_OPTIONS = [
        ("Next.js 16 + React 19", "nextjs"),
        ("React 18 + Vite", "react-vite"),
        ("Vue 3 + Nuxt", "vue-nuxt"),
        ("SvelteKit", "sveltekit"),
        ("Vanilla HTML/JS", "vanilla"),
        ("React Native + Expo", "react-native"),
    ]
    
    BACKEND_OPTIONS = [
        ("FastAPI (Python)", "fastapi"),
        ("Node.js + Express", "express"),
        ("Next.js API Routes", "nextjs-api"),
        ("Django", "django"),
        ("Go + Gin", "go-gin"),
        ("Rust + Axum", "rust-axum"),
        ("Serverless (AWS Lambda)", "serverless"),
    ]
    
    DATABASE_OPTIONS = [
        ("PostgreSQL", "postgres"),
        ("MySQL", "mysql"),
        ("MongoDB", "mongodb"),
        ("SQLite", "sqlite"),
        ("Redis", "redis"),
        ("Supabase", "supabase"),
        ("Firebase", "firebase"),
    ]
    
    AUTH_OPTIONS = [
        ("NextAuth.js", "nextauth"),
        ("Clerk", "clerk"),
        ("Auth0", "auth0"),
        ("Firebase Auth", "firebase-auth"),
        ("Custom JWT", "custom-jwt"),
        ("None (public app)", "none"),
    ]
    
    HOSTING_OPTIONS = [
        ("Vercel", "vercel"),
        ("Netlify", "netlify"),
        ("AWS", "aws"),
        ("Google Cloud", "gcp"),
        ("Railway", "railway"),
        ("Fly.io", "flyio"),
        ("Self-hosted", "self-hosted"),
    ]
    
    def __init__(self, planning_dir: Path):
        self.planning_dir = planning_dir
        self.data: Dict = {}
    
    def interactive_generate(self) -> str:
        """Generate project spec through interactive questions."""
        print("\n" + "="*60)
        print("🚀 GSD PROJECT GENERATOR")
        print("="*60)
        print("\nI'll ask you some questions to generate your PROJECT.md\n")
        
        # Basic info
        self.data["name"] = input("Project name: ").strip()
        while not self.data["name"]:
            print("❌ Project name is required")
            self.data["name"] = input("Project name: ").strip()
        
        self.data["vision"] = input("One-sentence description: ").strip()
        
        # Goals
        print("\n🎯 Goals (what are we building?)")
        print("   Enter goals one at a time, empty line to finish")
        self.data["goals"] = []
        while True:
            goal = input(f"   Goal {len(self.data['goals']) + 1}: ").strip()
            if not goal:
                break
            self.data["goals"].append(goal)
        
        # Target users
        self.data["target_users"] = input("\n👥 Target users: ").strip()
        
        # Tech stack
        print("\n🛠️  Tech Stack")
        self.data["frontend"] = self._select_option("Frontend", self.FRONTEND_OPTIONS)
        self.data["backend"] = self._select_option("Backend", self.BACKEND_OPTIONS)
        self.data["database"] = self._select_option("Database", self.DATABASE_OPTIONS)
        self.data["auth"] = self._select_option("Authentication", self.AUTH_OPTIONS)
        self.data["hosting"] = self._select_option("Hosting", self.HOSTING_OPTIONS)
        
        # Constraints
        print("\n⏱️  Constraints")
        self.data["timeline"] = input("   Timeline/deadline: ").strip() or "Not specified"
        
        print("   Any specific constraints? (empty line to finish)")
        self.data["constraints"] = []
        while True:
            constraint = input(f"   Constraint {len(self.data['constraints']) + 1}: ").strip()
            if not constraint:
                break
            self.data["constraints"].append(constraint)
        
        if not self.data["constraints"]:
            self.data["constraints"] = ["None specified"]
        
        # Definition of done
        print("\n✅ Definition of Done")
        print("   How will we know this is successful?")
        print("   Enter criteria one at a time, empty line to finish")
        self.data["definition_of_done"] = []
        while True:
            criterion = input(f"   Criterion {len(self.data['definition_of_done']) + 1}: ").strip()
            if not criterion:
                break
            self.data["definition_of_done"].append(criterion)
        
        if not self.data["definition_of_done"]:
            self.data["definition_of_done"] = ["Core features implemented", "Tests passing", "Deployed to production"]
        
        # Notes
        print("\n📝 Additional notes (optional): ")
        notes = input().strip()
        self.data["notes"] = notes if notes else None
        
        return self.generate_markdown()
    
    def _select_option(self, category: str, options: List[tuple]) -> str:
        """Present options and get selection."""
        print(f"\n   {category}:")
        for i, (name, value) in enumerate(options, 1):
            print(f"      {i}. {name}")
        print(f"      {len(options) + 1}. Other (specify)")
        
        while True:
            try:
                choice = input(f"   Select (1-{len(options) + 1}): ").strip()
                idx = int(choice) - 1
                
                if 0 <= idx < len(options):
                    return options[idx][0]
                elif idx == len(options):
                    return input("   Specify: ").strip()
                else:
                    print("   ❌ Invalid selection")
            except ValueError:
                print("   ❌ Please enter a number")
    
    def generate_markdown(self) -> str:
        """Generate PROJECT.md content from collected data."""
        lines = []
        
        lines.append(f"# {self.data['name']}")
        lines.append("")
        
        # Vision
        if self.data.get("vision"):
            lines.append("## Vision")
            lines.append("")
            lines.append(self.data["vision"])
            lines.append("")
        
        # Goals
        if self.data.get("goals"):
            lines.append("## Goals")
            lines.append("")
            for goal in self.data["goals"]:
                lines.append(f"1. {goal}")
            lines.append("")
        
        # Target Users
        if self.data.get("target_users"):
            lines.append("## Target Users")
            lines.append("")
            lines.append(self.data["target_users"])
            lines.append("")
        
        # Tech Stack
        lines.append("## Tech Stack")
        lines.append("")
        lines.append("| Layer | Technology |")
        lines.append("|-------|------------|")
        
        if self.data.get("frontend"):
            lines.append(f"| Frontend | {self.data['frontend']} |")
        if self.data.get("backend"):
            lines.append(f"| Backend | {self.data['backend']} |")
        if self.data.get("database"):
            lines.append(f"| Database | {self.data['database']} |")
        if self.data.get("auth"):
            lines.append(f"| Auth | {self.data['auth']} |")
        if self.data.get("hosting"):
            lines.append(f"| Hosting | {self.data['hosting']} |")
        
        lines.append("")
        
        # Constraints
        lines.append("## Constraints")
        lines.append("")
        lines.append(f"- **Timeline**: {self.data.get('timeline', 'Not specified')}")
        for constraint in self.data.get("constraints", []):
            if constraint != "None specified":
                lines.append(f"- {constraint}")
        lines.append("")
        
        # Definition of Done
        lines.append("## Definition of Done")
        lines.append("")
        for criterion in self.data.get("definition_of_done", []):
            lines.append(f"- [ ] {criterion}")
        lines.append("")
        
        # Notes
        if self.data.get("notes"):
            lines.append("## Notes")
            lines.append("")
            lines.append(self.data["notes"])
            lines.append("")
        
        # Metadata
        lines.append("---")
        lines.append("")
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        
        return "\n".join(lines)
    
    def quick_generate(self, name: str, description: str, stack: Dict) -> str:
        """Generate project spec from minimal input."""
        self.data = {
            "name": name,
            "vision": description,
            "goals": ["Build MVP"],
            "target_users": "TBD",
            "frontend": stack.get("frontend", "Next.js"),
            "backend": stack.get("backend", "FastAPI"),
            "database": stack.get("database", "PostgreSQL"),
            "auth": stack.get("auth", "NextAuth"),
            "hosting": stack.get("hosting", "Vercel"),
            "timeline": "TBD",
            "constraints": ["None specified"],
            "definition_of_done": ["Core features implemented", "Tests passing"],
        }
        
        return self.generate_markdown()
    
    def save(self, content: str) -> Path:
        """Save generated PROJECT.md."""
        project_file = self.planning_dir / "PROJECT.md"
        
        # Backup existing
        if project_file.exists():
            backup = self.planning_dir / f"PROJECT.md.backup.{datetime.now().strftime('%Y%m%d%H%M')}"
            backup.write_text(project_file.read_text())
            print(f"   📦 Backed up existing file to: {backup.name}")
        
        project_file.write_text(content)
        return project_file


def main():
    parser = argparse.ArgumentParser(
        description="Project Generator: Create PROJECT.md interactively",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Interactive mode
  %(prog)s --quick "My App" "A todo app" --stack nextjs,fastapi,postgres
        """
    )
    
    parser.add_argument("--dir", default=".", help="Project directory")
    parser.add_argument("--quick", metavar="NAME", help="Quick mode: project name")
    parser.add_argument("--description", help="Quick mode: description")
    parser.add_argument("--stack", help="Quick mode: stack (frontend,backend,database)")
    parser.add_argument("--output", type=Path, help="Output file (default: .planning/PROJECT.md)")
    
    args = parser.parse_args()
    
    project_path = Path(args.dir).resolve()
    planning_dir = project_path / ".planning"
    
    if not planning_dir.exists():
        print(f"❌ GSD not initialized in {project_path}")
        print(f"   Run: python3 scripts/init_gsd.py --dir {args.dir}")
        return 1
    
    generator = ProjectGenerator(planning_dir)
    
    if args.quick:
        # Quick mode
        stack = {}
        if args.stack:
            parts = args.stack.split(",")
            if len(parts) >= 1:
                stack["frontend"] = parts[0]
            if len(parts) >= 2:
                stack["backend"] = parts[1]
            if len(parts) >= 3:
                stack["database"] = parts[2]
        
        content = generator.quick_generate(args.quick, args.description or "", stack)
    else:
        # Interactive mode
        content = generator.interactive_generate()
    
    # Preview
    print("\n" + "="*60)
    print("📄 PREVIEW")
    print("="*60)
    print(content)
    print("="*60)
    
    # Confirm save
    confirm = input("\nSave this PROJECT.md? [Y/n]: ").strip().lower()
    if confirm in ['', 'y', 'yes']:
        output_path = generator.save(content)
        print(f"\n✅ PROJECT.md saved to: {output_path}")
        print(f"   Next: Edit REQUIREMENTS.md to define your phases")
    else:
        print("\n❌ Aborted. Output not saved.")
        # Still allow saving to custom location
        custom = input("Save to different location? [path/N]: ").strip()
        if custom and custom.lower() not in ['n', 'no']:
            Path(custom).write_text(content)
            print(f"✅ Saved to: {custom}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
