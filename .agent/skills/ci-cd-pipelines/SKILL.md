---
name: ci-cd-pipelines
description: |
  Continuous Integration and Deployment pipeline templates. GitHub Actions
  workflows for linting, testing, building, and deploying applications.
  Use when setting up CI/CD, creating workflows, or optimizing pipelines.
triggers:
  - Setting up CI/CD
  - Creating GitHub Actions workflows
  - Configuring automated testing
  - Setting up deployment pipelines
  - Optimizing build times
---

# CI/CD Pipelines

> **GitHub Actions workflows for automated testing and deployment**

## Quick Start

### Generate Workflow

```bash
python .agent/skills/ci-cd-pipelines/scripts/generate-workflow.py \
    --type python --deploy docker --output .github/workflows
```

Types: `python`, `node`, `fullstack`

### Manual Setup

Copy templates from `.agent/skills/ci-cd-pipelines/workflows/` to `.github/workflows/`.

---

## Workflow Types

### Python Project

```yaml
# .github/workflows/ci.yml
name: Python CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest ruff mypy
          
      - name: Lint
        run: ruff check .
        
      - name: Type check
        run: mypy .
        
      - name: Test
        run: pytest --cov=.
```

### Node.js Project

```yaml
# .github/workflows/ci.yml
name: Node.js CI

on: [push, pull_request]

jobs:
  test:
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
        
      - name: Test
        run: npm test
        
      - name: Build
        run: npm run build
```

---

## Caching

### Python

```yaml
- name: Cache pip packages
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

### Node.js

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'  # Automatic caching
```

---

## Deployment

### Docker Hub

```yaml
deploy:
  needs: test
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'
  
  steps:
    - uses: actions/checkout@v4
    
    - name: Login to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
        
    - name: Build and push
      run: |
        docker build -t ${{ secrets.DOCKER_USERNAME }}/myapp:${{ github.sha }} .
        docker push ${{ secrets.DOCKER_USERNAME }}/myapp:${{ github.sha }}
```

### Vercel

```yaml
deploy:
  needs: test
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'
  
  steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to Vercel
      uses: vercel/action-deploy@v1
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
        vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

---

## Secret Management

### GitHub Secrets

Set in: Settings → Secrets and variables → Actions

```yaml
env:
  API_KEY: ${{ secrets.API_KEY }}
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

### Environment Variables

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    env:
      NODE_ENV: test
      API_URL: http://localhost:3000
```

---

## Matrix Builds

```yaml
strategy:
  matrix:
    node-version: [18, 20, 21]
    os: [ubuntu-latest, windows-latest]

steps:
  - uses: actions/setup-node@v4
    with:
      node-version: ${{ matrix.node-version }}
```

---

## Workflow Templates

| Template | Purpose |
|----------|---------|
| [python.yml](workflows/python.yml) | Python lint, test, build |
| [nodejs.yml](workflows/nodejs.yml) | Node.js lint, test, build |
| [fullstack.yml](workflows/fullstack.yml) | Multi-service deployment |

---

## Generator

```bash
# Generate Python workflow
python scripts/generate-workflow.py --type python --output .github/workflows

# With Docker deployment
python scripts/generate-workflow.py --type python --deploy docker --output .github/workflows

# With Vercel deployment
python scripts/generate-workflow.py --type node --deploy vercel --output .github/workflows
```

---

## Best Practices

- **Pin actions**: Use `@v4` not `@master`
- **Fail fast**: Cancel other jobs if one fails
- **Parallel jobs**: Split lint/test/build
- **Conditional deploy**: Only on main branch
- **Secrets**: Never hardcode, use GitHub Secrets
- **Caching**: Always cache dependencies

---

## References

| File | Description |
|------|-------------|
| [secret-management.md](references/secret-management.md) | Managing secrets securely |

---

## Anti-Patterns

❌ **Running on every commit**: Use path filters  
❌ **No timeouts**: Set `timeout-minutes`  
❌ **Broad permissions**: Use minimal permissions  
❌ **Storing artifacts forever**: Set retention  
❌ **No notifications**: Alert on failure
