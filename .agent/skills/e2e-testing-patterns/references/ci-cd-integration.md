# CI/CD Integration

> GitHub Actions workflows for Playwright E2E tests

## Basic Workflow

```yaml
# .github/workflows/e2e.yml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight

jobs:
  test:
    timeout-minutes: 60
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
      
      - name: Install Playwright browsers
        run: npx playwright install --with-deps
      
      - name: Run Playwright tests
        run: npx playwright test
        env:
          BASE_URL: ${{ secrets.STAGING_URL }}
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: |
            playwright-report/
            test-results/
          retention-days: 30
```

## Parallel Execution with Sharding

```yaml
jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        shard: [1/4, 2/4, 3/4, 4/4]
    
    steps:
      # ... setup steps
      
      - name: Run tests (shard ${{ matrix.shard }})
        run: npx playwright test --shard=${{ matrix.shard }}
```

## Testing Against Preview Deployments

```yaml
name: E2E on Preview

on:
  deployment_status:
    types: [created]

jobs:
  test:
    if: github.event.deployment_status.state == 'success'
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Install dependencies
        run: npm ci
      
      - name: Install Playwright
        run: npx playwright install --with-deps
      
      - name: Run tests against preview
        run: npx playwright test
        env:
          BASE_URL: ${{ github.event.deployment_status.target_url }}
```

## Multi-Environment Testing

```yaml
name: E2E Multi-Environment

on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options:
          - staging
          - production

jobs:
  test:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment }}
    
    steps:
      # ... setup
      
      - name: Run tests
        run: npx playwright test
        env:
          BASE_URL: ${{ vars.BASE_URL }}
          API_KEY: ${{ secrets.API_KEY }}
```

## With Database Setup

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    
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
      
      - name: Setup application
        run: |
          npm ci
          npm run db:migrate
          npm run db:seed
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test
      
      - name: Start application
        run: npm start &
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test
      
      - name: Wait for app
        run: npx wait-on http://localhost:3000 --timeout 60000
      
      - name: Run E2E tests
        run: npx playwright test
        env:
          BASE_URL: http://localhost:3000
```

## Slack Notifications

```yaml
- name: Notify Slack
  if: always()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "E2E Tests: ${{ job.status }}",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*E2E Test Results*\nStatus: ${{ job.status }}\nBranch: ${{ github.ref }}\nCommit: ${{ github.sha }}"
            }
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## Reporting to Test Management

```yaml
- name: Publish Test Report
  if: always()
  uses: dorny/test-reporter@v1
  with:
    name: Playwright Tests
    path: test-results/*.xml
    reporter: junit
    fail-on-error: false
```

## Performance Budget

```yaml
- name: Run performance tests
  run: npx playwright test --grep @performance

- name: Check performance budget
  run: |
    DURATION=$(cat test-results/performance.json | jq '.duration')
    if [ $DURATION -gt 5000 ]; then
      echo "Performance budget exceeded: ${DURATION}ms > 5000ms"
      exit 1
    fi
```

## Best Practices

1. **Use secrets for credentials**: Never hardcode passwords
2. **Artifact retention**: Keep reports for 30 days
3. **Fail fast**: Set appropriate timeouts
4. **Notifications**: Alert on failure only
5. **Parallel jobs**: Use sharding for large suites
6. **Retry logic**: Configure in playwright.config.ts, not CI

## Troubleshooting

### Flaky Tests in CI

```yaml
- name: Run tests with retry
  run: npx playwright test --retries=2
```

### Debugging Failures

```yaml
- name: Upload traces
  if: failure()
  uses: actions/upload-artifact@v4
  with:
    name: failure-traces
    path: test-results/
```

### Timeout Issues

```yaml
jobs:
  test:
    timeout-minutes: 30  # Increase if needed
    
    steps:
      - name: Run tests
        run: npx playwright test
        timeout-minutes: 25  # Slightly less than job timeout
```
