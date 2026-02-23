---
name: cloud-deployment
description: |
  Cloud deployment guides for major platforms. Step-by-step instructions for
  deploying to Vercel, AWS, Railway. Environment configuration, custom domains,
  and SSL setup. Use when deploying applications to the cloud.
triggers:
  - Deploying application
  - Setting up custom domain
  - Configuring SSL/TLS
  - Environment setup
  - Platform selection
---

# Cloud Deployment

> **Deployment guides for Vercel, AWS, and Railway**

## Quick Start

### Choose Your Platform

| Platform | Best For | Complexity |
|----------|----------|------------|
| [Vercel](guides/vercel.md) | Next.js, static sites | Easy |
| [Railway](guides/railway.md) | Full-stack, containers | Easy |
| [AWS](guides/aws.md) | Enterprise, scale | Complex |

### One-Command Deploy

```bash
# Vercel (Next.js)
npx vercel --prod

# Railway
railway up

# AWS (with CDK)
cdk deploy
```

---

## Platform Comparison

| Feature | Vercel | Railway | AWS |
|---------|--------|---------|-----|
| Next.js | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| Static sites | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Full-stack | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Databases | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Serverless | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Cost (start) | Free | Free | Free tier |
| Cost (scale) | $$ | $$ | $-$$$ |

---

## Environment Configuration

### 12-Factor App

```bash
# Development
DATABASE_URL=postgresql://localhost:5432/dev
DEBUG=true

# Staging
DATABASE_URL=postgresql://staging-db:5432/app
DEBUG=false

# Production
DATABASE_URL=postgresql://prod-db:5432/app
DEBUG=false
```

### Platform Environment Variables

| Platform | Setup Location |
|----------|---------------|
| Vercel | Dashboard → Settings → Environment Variables |
| Railway | Dashboard → Variables |
| AWS | Parameter Store / Secrets Manager |

---

## Custom Domains

### Vercel

1. Buy domain or use existing
2. Add domain in Vercel dashboard
3. Update DNS records
4. SSL auto-provisioned

### Railway

1. Go to project settings
2. Add custom domain
3. Update DNS CNAME
4. SSL auto-provisioned

### AWS

1. Register domain in Route 53
2. Create CloudFront distribution
3. Add SSL certificate (ACM)
4. Update DNS records

---

## Deployment Checklist

Before deploying:

- [ ] Environment variables set
- [ ] Database migrations ready
- [ ] Health check endpoint working
- [ ] Logs configured
- [ ] Domain configured (if needed)
- [ ] SSL enabled
- [ ] Error tracking setup

---

## Guides

| Guide | Platform | Use Case |
|-------|----------|----------|
| [vercel.md](guides/vercel.md) | Vercel | Next.js, React |
| [railway.md](guides/railway.md) | Railway | Full-stack apps |
| [aws.md](guides/aws.md) | AWS | Enterprise, scale |

---

## References

| File | Description |
|------|-------------|
| [environment-config.md](references/environment-config.md) | Multi-environment setup |
| [domain-ssl.md](references/domain-ssl.md) | Custom domains, SSL |

---

## Cost Optimization

### Vercel
- Use static generation when possible
- Limit serverless function duration
- Monitor bandwidth usage

### Railway
- Use hobby plan for development
- Scale vertically before horizontally
- Monitor resource usage

### AWS
- Use reserved instances for steady workloads
- Set up billing alerts
- Clean up unused resources
- Use Spot instances for background jobs
