# Production Deployment Checklist

> Verify your containers are production-ready

## Pre-Deployment

### Image Security

- [ ] Non-root user configured (`USER` instruction)
- [ ] Minimal base image used (alpine/slim/distroless)
- [ ] No secrets in image (use env vars/secrets)
- [ ] Image scanned for vulnerabilities (`docker scan` or Trivy)
- [ ] `.dockerignore` configured

### Image Optimization

- [ ] Multi-stage build implemented
- [ ] Image size < 200MB (microservices)
- [ ] Layer caching optimized
- [ ] No unnecessary packages
- [ ] Build cache cleaned up

### Health & Monitoring

- [ ] Health check defined (`HEALTHCHECK`)
- [ ] Graceful shutdown handling (SIGTERM)
- [ ] Logging configured (structured JSON)
- [ ] Error tracking integrated

## Runtime Configuration

### Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 128M
```

- [ ] CPU limits set
- [ ] Memory limits set
- [ ] Swap limits configured

### Security

- [ ] Read-only filesystem (`--read-only`)
- [ ] No new privileges (`--security-opt=no-new-privileges`)
- [ ] Drop all capabilities
- [ ] User namespace remapping (if possible)

### Networking

- [ ] Internal networks for databases
- [ ] No exposed ports that shouldn't be public
- [ ] TLS/SSL for external connections

## Environment

### Configuration

- [ ] Environment variables documented
- [ ] Secrets managed (not in code/env files)
- [ ] Different configs per environment (dev/staging/prod)
- [ ] Feature flags configured

### Database

- [ ] Migration strategy defined
- [ ] Backup strategy in place
- [ ] Connection pooling configured
- [ ] Database credentials rotated

## Deployment

### Process

- [ ] Zero-downtime deployment strategy
- [ ] Rollback procedure documented
- [ ] Health checks passing before routing traffic
- [ ] Gradual rollout (canary/blue-green)

### Monitoring

- [ ] Application metrics collected
- [ ] Infrastructure metrics collected
- [ ] Alerting rules configured
- [ ] Log aggregation configured
- [ ] Dashboard created

### Scaling

- [ ] Horizontal scaling tested
- [ ] Auto-scaling configured
- [ ] Load balancer configured
- [ ] Session handling (stateless)

## Post-Deployment

### Verification

- [ ] Smoke tests passing
- [ ] Critical user journeys working
- [ ] Performance acceptable
- [ ] Error rates normal

### Documentation

- [ ] Deployment process documented
- [ ] Runbook created
- [ ] On-call procedures defined
- [ ] Incident response plan ready

## Security Checklist

### Container Security

```bash
# Run as non-root
docker run --user 1000:1000 myapp

# Read-only filesystem
docker run --read-only --tmpfs /tmp myapp

# No new privileges
docker run --security-opt=no-new-privileges:true myapp

# Drop capabilities
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE myapp
```

### Network Security

- [ ] Firewall rules configured
- [ ] Network segmentation (app/db separation)
- [ ] TLS for all external connections
- [ ] Service mesh (if applicable)

## Performance Checklist

### Startup Time

- [ ] Container starts in < 10 seconds
- [ ] Health check passes quickly
- [ ] No unnecessary initialization

### Resource Usage

- [ ] CPU usage < 70% at peak
- [ ] Memory usage < 80% of limit
- [ ] Disk I/O optimized
- [ ] Network latency acceptable

## Disaster Recovery

- [ ] Backup strategy tested
- [ ] Recovery time objective (RTO) defined
- [ ] Recovery point objective (RPO) defined
- [ ] DR plan documented and tested

## Cost Optimization

- [ ] Right-sized instances
- [ ] Spot/preemptible instances for non-critical
- [ ] Auto-scaling configured
- [ ] Unused resources cleaned up
- [ ] Reserved capacity (if applicable)

---

## Quick Verification Script

```bash
#!/bin/bash

echo "=== Production Checklist Verification ==="

# Check non-root user
echo "Checking for non-root user..."
docker inspect myapp:latest | grep -q '"User": "root"' && echo "❌ Running as root" || echo "✅ Non-root user"

# Check image size
echo "Checking image size..."
SIZE=$(docker images myapp:latest --format "{{.Size}}" | sed 's/MB//')
if [ "$SIZE" -lt 200 ]; then
    echo "✅ Image size OK ($SIZE MB)"
else
    echo "⚠️ Image large ($SIZE MB)"
fi

# Check health check
echo "Checking health check..."
docker inspect myapp:latest | grep -q "Healthcheck" && echo "✅ Health check defined" || echo "❌ No health check"

echo "=== Verification Complete ==="
```
