# Environment Configuration

> Managing development, staging, and production environments

## Environment Types

| Environment | Purpose | Data |
|-------------|---------|------|
| Development | Local development | Synthetic/sample |
| Staging | Pre-production testing | Production-like |
| Production | Live application | Real user data |

## Configuration Strategy

### 12-Factor App Method

```bash
# Store config in environment variables
DATABASE_URL=postgresql://localhost:5432/dev
API_KEY=dev-key-xxx
DEBUG=true
```

### File-Based (Not Recommended)

```yaml
# config/environments/development.yml (AVOID)
database:
  url: postgresql://localhost:5432/dev
```

## Platform-Specific Setup

### Vercel

```bash
# Development
vercel env add DATABASE_URL development

# Preview (PRs)
vercel env add DATABASE_URL preview

# Production
vercel env add DATABASE_URL production
```

### Railway

```bash
# Set for all environments
railway variables set DATABASE_URL=...

# Per environment in dashboard
```

### AWS

```bash
# Parameter Store (development)
aws ssm put-parameter --name /myapp/dev/db --value "..." --type SecureString

# Parameter Store (production)
aws ssm put-parameter --name /myapp/prod/db --value "..." --type SecureString
```

## Environment Files

### .env.example

```bash
# Copy to .env.local for development
DATABASE_URL=postgresql://localhost:5432/myapp
REDIS_URL=redis://localhost:6379
API_KEY=your-api-key
DEBUG=true
```

### .env.local (Git-ignored)

```bash
# Local development only
DATABASE_URL=postgresql://localhost:5432/myapp
```

### Loading in Application

**Python:**
```python
from dotenv import load_dotenv
load_dotenv()  # Loads .env.local

database_url = os.getenv('DATABASE_URL')
```

**Node.js:**
```javascript
require('dotenv').config()

const databaseUrl = process.env.DATABASE_URL
```

## Feature Flags

### Simple Environment Variable

```javascript
const features = {
  newDashboard: process.env.ENABLE_NEW_DASHBOARD === 'true',
  betaFeature: process.env.ENABLE_BETA === 'true'
}
```

### Feature Flag Service

```javascript
// Using LaunchDarkly or similar
import { init } from 'launchdarkly-node-server-sdk'

const client = init(process.env.LD_SDK_KEY)
const showFeature = await client.variation('new-feature', user, false)
```

## Database Per Environment

| Environment | Database | Access |
|-------------|----------|--------|
| Development | Local PostgreSQL | Developer only |
| Staging | RDS staging | Team only |
| Production | RDS production | Limited access |

### Migration Strategy

```bash
# Development
alembic upgrade head

# Staging (before deploy)
railway run alembic upgrade head

# Production (during maintenance window)
railway run --environment production alembic upgrade head
```

## Testing in Production

### Canary Deployments

Deploy to subset of users:

```javascript
if (user.id % 10 === 0) {
  // New version
} else {
  // Old version
}
```

### Feature Flags

```javascript
if (isEnabled('new-checkout', user)) {
  return <NewCheckout />
}
return <OldCheckout />
```

## Environment Checklist

### Development

- [ ] Local database running
- [ ] Hot reload enabled
- [ ] Debug logging on
- [ ] Test data seeded

### Staging

- [ ] Production-like data
- [ ] Same infrastructure
- [ ] SSL enabled
- [ ] Automated deployments

### Production

- [ ] SSL enforced
- [ ] CDN configured
- [ ] Monitoring enabled
- [ ] Backups automated
- [ ] Alerting configured

## Security

### Never Commit

```gitignore
.env
.env.local
.env.*.local
secrets/
*.pem
```

### Rotate Regularly

- API keys: Every 90 days
- Database passwords: Every 180 days
- SSL certificates: Auto-renew

## Cost Management

| Environment | Strategy | Example |
|-------------|----------|---------|
| Development | Local/free tier | Docker locally |
| Staging | Small instances | 1 vCPU, 1GB RAM |
| Production | Right-sized | Based on load |
