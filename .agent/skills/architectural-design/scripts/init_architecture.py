#!/usr/bin/env python3
import os
import sys
import argparse
import json

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
PLANNING_DIR = "docs/planning"

def load_template(filename):
    path = os.path.join(TEMPLATE_DIR, filename)
    if not os.path.exists(path):
        print(f"Error: Template {filename} not found at {path}")
        sys.exit(1)
    with open(path, "r") as f:
        return f.read()

def main():
    parser = argparse.ArgumentParser(description="Initialize architectural planning documents.")
    parser.add_argument("--project-name", help="Name of the project")
    parser.add_argument("--goal", help="Detailed goal of the project")
    parser.add_argument("--tech-stack", help="Tech stack list")
    parser.add_argument("--constraints", help="System constraints (infra, budget, security)")
    parser.add_argument("--erd", help="ERD diagram content")
    parser.add_argument("--schema", help="Schema definitions")
    parser.add_argument("--api", help="API endpoints")
    parser.add_argument("--middleware", help="Auth middleware strategy")
    parser.add_argument("--rls", help="Row Level Security policies")
    
    args = parser.parse_args()

    # Defaults / Prompts
    project_name = args.project_name or input("Project Name: ")
    goal = args.goal or input("Project Goal: ")
    tech_stack = args.tech_stack or input("Tech Stack: ")
    constraints = args.constraints or input("Constraints: ") # expects JSON string or raw text if simple
    
    # Process constraints if JSON string, else treat as raw text for simplicity in template
    # For now, simplistic approach: just use the string.
    
    # Defaults for optional fields if not provided
    erd = args.erd or "N/A"
    schema = args.schema or "N/A"
    api = args.api or "N/A"
    middleware = args.middleware or "N/A"
    rls = args.rls or "N/A"

    # Context for template rendering
    context = {
        "project_name": project_name,
        "goal": goal,
        "tech_stack_list": tech_stack,
        "infrastructure_constraints": "See detailed plan.", # Placeholder if not passed individually
        "budget_constraints": "See detailed plan.",
        "security_constraints": "See detailed plan.",
        "erd_diagram": erd,
        "schema_definitions": schema,
        "api_endpoints": api,
        "middleware_strategy": middleware,
        "rls_policies": rls,
        "tasks_backlog": "- [ ] Define initial tasks based on PLAN.md" 
    }
    
    # Update constraints if passed as a single block (simplification for the prompt)
    # The template expects infrastructure_constraints, etc. separately.
    # The script should really parse these out or just take them as arguments.
    # Given the complexity, I'll update the script to take a JSON config via --config-file or similar if robust.
    # But for this task, I will just map the known Phase 2 requirements directly into the defaults if not provided, 
    # OR better, allow all inputs.
    
    if args.constraints:
       context["infrastructure_constraints"] = args.constraints
       context["budget_constraints"] = args.constraints
       context["security_constraints"] = args.constraints

    # Create directory
    if not os.path.exists(PLANNING_DIR):
        print(f"Creating directory {PLANNING_DIR}...")
        os.makedirs(PLANNING_DIR)

    # Render and Write PLAN.md
    plan_content = load_template("PLAN.md")
    for key, value in context.items():
        plan_content = plan_content.replace(f"{{{{ {key} }}}}", value)
    
    with open(os.path.join(PLANNING_DIR, "PLAN.md"), "w") as f:
        f.write(plan_content)
    print(f"Generated {PLANNING_DIR}/PLAN.md")

    # Render and Write TASKS.md
    tasks_content = load_template("TASKS.md")
    for key, value in context.items():
        tasks_content = tasks_content.replace(f"{{{{ {key} }}}}", value)

    with open(os.path.join(PLANNING_DIR, "TASKS.md"), "w") as f:
        f.write(tasks_content)
    print(f"Generated {PLANNING_DIR}/TASKS.md")

if __name__ == "__main__":
    main()
