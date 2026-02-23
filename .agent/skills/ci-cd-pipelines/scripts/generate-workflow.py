#!/usr/bin/env python3
"""
Generate GitHub Actions workflow files.

Usage:
    python generate-workflow.py --type python --output .github/workflows
    python generate-workflow.py --type node --deploy vercel --output .github/workflows

Types: python, node, fullstack
Deploy: none, docker, vercel, railway
"""

import argparse
import sys
from pathlib import Path


PYTHON_WORKFLOW = '''name: Python CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Cache pip packages
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: {{{{ runner.os }}}}-pip-${{{{ hashFiles('**/requirements.txt') }}}}
          
      - name: Install dependencies
        run: |
          pip install ruff mypy
          pip install -r requirements.txt
          
      - name: Lint with ruff
        run: ruff check .
        
      - name: Type check with mypy
        run: mypy .

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Cache pip packages
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: {{{{ runner.os }}}}-pip-${{{{ hashFiles('**/requirements.txt') }}}}
          
      - name: Install dependencies
        run: |
          pip install pytest pytest-cov
          pip install -r requirements.txt
          
      - name: Run tests
        run: pytest --cov=. --cov-report=xml
        
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: false

{deploy_job}
'''


NODE_WORKFLOW = '''name: Node.js CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Lint
        run: npm run lint
        
      - name: Type check
        run: npm run type-check

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Run tests
        run: npm test -- --coverage
        
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          fail_ci_if_error: false

  build:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Build
        run: npm run build
        
      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: build
          path: dist/
          retention-days: 7

{deploy_job}
'''


FULLSTACK_WORKFLOW = '''name: Full-Stack CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint-backend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install ruff mypy
      - run: ruff check .
      - run: mypy .

  lint-frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint

  test-backend:
    runs-on: ubuntu-latest
    needs: lint-backend
    defaults:
      run:
        working-directory: ./backend
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pytest
      - run: pip install -r requirements.txt
      - run: pytest
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test

  test-frontend:
    runs-on: ubuntu-latest
    needs: lint-frontend
    defaults:
      run:
        working-directory: ./frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm test

{deploy_job}
'''


def get_docker_deploy_job() -> str:
    return '''  deploy:
    runs-on: ubuntu-latest
    needs: [test, build]
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKER_USERNAME }}/${{ github.event.repository.name }}:latest
            ${{ secrets.DOCKER_USERNAME }}/${{ github.event.repository.name }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
'''


def get_vercel_deploy_job() -> str:
    return '''  deploy:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
'''


def get_railway_deploy_job() -> str:
    return '''  deploy:
    runs-on: ubuntu-latest
    needs: [test, build]
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Railway CLI
        run: npm install -g @railway/cli
      
      - name: Deploy to Railway
        run: railway up --service ${{ github.event.repository.name }}
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
'''


def generate_workflow(project_type: str, deploy_type: str, output_dir: str):
    """Generate workflow file."""
    
    templates = {
        'python': PYTHON_WORKFLOW,
        'node': NODE_WORKFLOW,
        'fullstack': FULLSTACK_WORKFLOW,
    }
    
    if project_type not in templates:
        print(f"Error: Unknown type '{project_type}'. Use: {', '.join(templates.keys())}")
        sys.exit(1)
    
    # Get deploy job
    deploy_jobs = {
        'none': '',
        'docker': get_docker_deploy_job(),
        'vercel': get_vercel_deploy_job(),
        'railway': get_railway_deploy_job(),
    }
    
    deploy_job = deploy_jobs.get(deploy_type, '')
    
    # Generate content
    template = templates[project_type]
    workflow_content = template.format(deploy_job=deploy_job)
    
    # Write file
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    
    workflow_path = output / f'{project_type}-ci.yml'
    workflow_path.write_text(workflow_content)
    
    print(f"✅ Created: {workflow_path}")
    
    # Print next steps
    print(f"\n🎉 Generated GitHub Actions workflow for '{project_type}'!")
    print(f"\nNext steps:")
    print(f"  1. Review the workflow: {workflow_path}")
    print(f"  2. Add required secrets to GitHub:")
    if deploy_type == 'docker':
        print(f"     - DOCKER_USERNAME")
        print(f"     - DOCKER_PASSWORD")
    elif deploy_type == 'vercel':
        print(f"     - VERCEL_TOKEN")
        print(f"     - VERCEL_ORG_ID")
        print(f"     - VERCEL_PROJECT_ID")
    elif deploy_type == 'railway':
        print(f"     - RAILWAY_TOKEN")
    print(f"  3. Commit and push to trigger workflow")
    print(f"  4. Check Actions tab in GitHub repo")


def main():
    parser = argparse.ArgumentParser(
        description="Generate GitHub Actions workflow files"
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=['python', 'node', 'fullstack'],
        help="Project type"
    )
    parser.add_argument(
        "--deploy",
        default='none',
        choices=['none', 'docker', 'vercel', 'railway'],
        help="Deployment target (default: none)"
    )
    parser.add_argument(
        "--output",
        default=".github/workflows",
        help="Output directory (default: .github/workflows)"
    )
    
    args = parser.parse_args()
    
    generate_workflow(args.type, args.deploy, args.output)


if __name__ == "__main__":
    main()
