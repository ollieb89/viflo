# Secret Management

> Best practices for managing secrets in CI/CD pipelines

## GitHub Secrets

### Setting Secrets

Navigate to: **Settings → Secrets and variables → Actions**

### Repository Secrets

Available to all workflows in the repository:

```yaml
env:
  API_KEY: ${{ secrets.API_KEY }}
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

### Environment Secrets

Available only to specific environments:

```yaml
jobs:
  deploy:
    environment: production
    steps:
      - run: echo ${{ secrets.PROD_DATABASE_URL }}
```

### Organization Secrets

Available to all repositories in the organization:
- Navigate to: Organization → Settings → Secrets

## Best Practices

### 1. Never Hardcode Secrets

```yaml
# ❌ Bad
env:
  API_KEY: "sk-1234567890abcdef"

# ✅ Good
env:
  API_KEY: ${{ secrets.API_KEY }}
```

### 2. Use Specific Secrets

```yaml
# ❌ Bad: Same secret for all environments
DATABASE_URL: ${{ secrets.DATABASE_URL }}

# ✅ Good: Environment-specific secrets
DATABASE_URL: ${{ secrets.STAGING_DATABASE_URL }}
DATABASE_URL: ${{ secrets.PROD_DATABASE_URL }}
```

### 3. Rotate Regularly

- Set calendar reminders
- Rotate after employee departure
- Rotate after suspected breach
- Use short-lived tokens when possible

### 4. Least Privilege

- Only grant necessary permissions
- Use environment-specific secrets
- Limit secret scope

## Secret Types

### Database Credentials

```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
```

### Cloud Provider

```yaml
# AWS
env:
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

# Vercel
env:
  VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
  VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
  VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}

# Railway
env:
  RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

### Docker Registry

```yaml
env:
  DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
  DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
```

## Alternative: Doppler

For centralized secret management:

```yaml
jobs:
  deploy:
    steps:
      - uses: dopplerhq/cli-action@v1
      - run: doppler secrets download --format docker > .env
        env:
          DOPPLER_TOKEN: ${{ secrets.DOPPLER_TOKEN }}
```

## Secret Scanning

Enable secret scanning in GitHub:

**Settings → Security → Code security → Secret scanning**

## Recovery

If a secret is leaked:

1. Revoke the secret immediately
2. Generate new secret
3. Update in GitHub Secrets
4. Rotate any dependent secrets
5. Review access logs

## Audit Trail

GitHub logs secret access:

**Settings → Security → Audit log**

Monitor for:
- Unauthorized access
- Unusual patterns
- Failed authentication attempts
