# Domain and SSL Setup

> Custom domain configuration and SSL/TLS certificates

## Domain Setup Overview

```
User → Domain Registrar → DNS → CDN/Load Balancer → Application
```

## Domain Registration

### Popular Registrars

| Registrar | Price | Features |
|-----------|-------|----------|
| Cloudflare | Wholesale | Free privacy, fast DNS |
| Namecheap | $9-15/yr | Free WHOIS privacy |
| Google Domains | $12/yr | Simple, integrated |
| AWS Route 53 | $12/yr | Integrated with AWS |

### DNS Configuration

#### A Record (Root domain)

```
Type: A
Name: @ (or leave blank)
Value: 76.76.21.21  # Vercel example
TTL: 3600
```

#### CNAME (Subdomain)

```
Type: CNAME
Name: www
Value: cname.vercel-dns.com
TTL: 3600
```

#### ALIAS/ANAME (Root with CNAME-like)

Some providers support ALIAS for root domain:

```
Type: ALIAS
Name: @
Value: myapp.vercel.app
```

## SSL/TLS Certificates

### Types

| Type | Validation | Use Case |
|------|-----------|----------|
| DV (Domain Validated) | Domain ownership | Most websites |
| OV (Organization Validated) | Organization | Business sites |
| EV (Extended Validated) | Extended checks | Banks, high-trust |

### Providers

| Provider | Cost | Automation |
|----------|------|------------|
| Let's Encrypt | Free | ACME protocol |
| Cloudflare | Free | Automatic |
| AWS ACM | Free | Automatic |
| DigiCert | $$$ | Manual |

## Platform-Specific SSL

### Vercel

SSL is automatic when you add a custom domain.

```bash
# Add domain
vercel domains add myapp.com

# Status
vercel domains inspect myapp.com
```

### Railway

SSL auto-provisioned for custom domains.

Dashboard → Service → Settings → Domains → Add

### AWS (ACM)

```bash
# Request certificate
aws acm request-certificate \
  --domain-name example.com \
  --subject-alternative-names www.example.com \
  --validation-method DNS

# Add validation records to Route 53
```

## Redirects

### www to Root (or vice versa)

**Vercel (vercel.json):**
```json
{
  "redirects": [
    {
      "source": "www.example.com/:path*",
      "destination": "https://example.com/:path*"
    }
  ]
}
```

**Nginx:**
```nginx
server {
  listen 80;
  server_name www.example.com;
  return 301 $scheme://example.com$request_uri;
}
```

### HTTP to HTTPS

**Vercel:** Automatic

**Nginx:**
```nginx
server {
  listen 80;
  return 301 https://$host$request_uri;
}
```

## Subdomains

### Common Patterns

| Subdomain | Purpose |
|-----------|---------|
| www | Main site |
| app | Application |
| api | API endpoints |
| admin | Admin panel |
| blog | Blog/CMS |
| staging | Staging environment |

### Setup

```
Type: CNAME
Name: api
Value: api.myapp.com.herokudns.com
```

## Troubleshooting

### DNS Propagation

Check propagation:
```bash
dig +short example.com
nslookup example.com
# Or online: whatsmydns.net
```

Takes 24-48 hours max, usually minutes.

### SSL Issues

**Certificate not valid:**
- Check domain matches certificate
- Verify intermediate certificates
- Check expiration date

**Mixed content:**
- Ensure all resources use HTTPS
- Update hardcoded HTTP URLs

### Common Errors

| Error | Solution |
|-------|----------|
| DNS_PROBE_FINISHED_NXDOMAIN | DNS not propagated |
| ERR_SSL_PROTOCOL_ERROR | SSL not configured |
| 404 after DNS change | Check hosting configuration |

## Best Practices

1. **Use HTTPS everywhere**: Redirect HTTP to HTTPS
2. **HSTS headers**: Enforce HTTPS
3. **Renewal**: Automate certificate renewal
4. **Monitoring**: Set up SSL expiry alerts
5. **Backup**: Have rollback DNS records

## Checklist

- [ ] Domain registered
- [ ] DNS records configured
- [ ] SSL certificate issued
- [ ] HTTPS redirect enabled
- [ ] www redirect configured
- [ ] Certificate auto-renewal set up
- [ ] SSL monitoring enabled
