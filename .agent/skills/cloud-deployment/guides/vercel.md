# Vercel Deployment Guide

> Deploy Next.js and frontend applications to Vercel

## Quick Start

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel

# Deploy to production
vercel --prod
```

## Project Setup

### 1. Connect Repository

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import Git repository
4. Select framework preset (Next.js)

### 2. Configure Build

```json
// vercel.json (optional)
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "regions": ["iad1"]
}
```

### 3. Environment Variables

```bash
# Set via CLI
vercel env add DATABASE_URL

# Or in dashboard:
# Settings → Environment Variables
```

## Next.js Specific

### Static Site Generation (SSG)

```javascript
// next.config.js
module.exports = {
  output: 'export',  // Static HTML export
  distDir: 'dist',
}
```

### Server-Side Rendering (SSR)

Default for Next.js. No config needed.

### API Routes

```javascript
// pages/api/hello.js
export default function handler(req, res) {
  res.status(200).json({ message: 'Hello' })
}
```

## Custom Domain

### Step 1: Add Domain

Dashboard → Project → Settings → Domains → Add

### Step 2: Configure DNS

**Option A: Nameservers (recommended)**
```
Type: NS
Name: @
Value: ns1.vercel-dns.com
```

**Option B: A Record**
```
Type: A
Name: @
Value: 76.76.21.21
```

**Option C: CNAME (subdomains)**
```
Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

### Step 3: SSL

SSL auto-provisioned. Status in dashboard.

## Environment Variables

### Per Environment

```bash
# Development
vercel env add DATABASE_URL development

# Preview
vercel env add DATABASE_URL preview

# Production
vercel env add DATABASE_URL production
```

### From .env.local

```bash
# Load all variables from .env.local
vercel env pull
```

## Preview Deployments

Every push creates a preview deployment:

```bash
# Deploy preview
vercel

# Get preview URL
vercel --confirm
```

## Serverless Functions

```javascript
// api/users.js
export default async function handler(req, res) {
  const users = await fetchUsers()
  res.status(200).json(users)
}
```

Config:
```json
{
  "functions": {
    "api/users.js": {
      "memory": 1024,
      "maxDuration": 10
    }
  }
}
```

## Edge Functions

```javascript
// middleware.js
import { NextResponse } from 'next/server'

export function middleware(request) {
  // Run at edge
  return NextResponse.next()
}

export const config = {
  matcher: '/api/:path*',
}
```

## Troubleshooting

### Build Failures

```bash
# Local build test
vercel build

# Check logs
vercel logs --all
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Out of memory | Increase memory in vercel.json |
| Timeout | Reduce function duration or split |
| Build error | Check buildCommand in vercel.json |

## Pricing

| Plan | Cost | Limits |
|------|------|--------|
| Hobby | Free | 100GB bandwidth |
| Pro | $20/mo | 1TB bandwidth |
| Enterprise | Custom | Custom |

## Best Practices

1. **Use environment variables**: Never hardcode secrets
2. **Optimize images**: Use next/image
3. **Static when possible**: Use SSG over SSR
4. **Monitor usage**: Check bandwidth and function invocations
5. **Use preview deployments**: Test before production
