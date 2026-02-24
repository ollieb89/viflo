# API Security Checklist

Extracted from [SKILL.md](../../SKILL.md)

## Authentication & Authorization

- [ ] **JWT Implementation**
  - Use strong signing algorithms (RS256, HS256)
  - Set appropriate expiration times (access: 15m, refresh: 7d)
  - Store tokens securely (httpOnly cookies for web)
  - Implement token refresh mechanism
  - Validate token on every protected request

- [ ] **Password Security**
  - Hash with bcrypt (cost factor 10-12) or Argon2
  - Enforce minimum password complexity
  - Implement password reset with secure tokens
  - Rate limit login attempts
  - Never return passwords in API responses

- [ ] **Role-Based Access Control**
  - Define clear roles and permissions
  - Implement middleware for role checking
  - Validate permissions at both middleware and service layers
  - Use principle of least privilege

## Input Validation & Sanitization

- [ ] **Request Validation**
  - Validate all inputs (body, query, params)
  - Use schema validation (Zod, Joi, JSON Schema)
  - Reject unexpected fields (stripUnknown: true)
  - Validate content types
  - Set maximum request size limits

- [ ] **SQL Injection Prevention**
  - Use parameterized queries/prepared statements
  - Avoid string concatenation in SQL
  - Use ORM query builders
  - Validate and sanitize table/column names

- [ ] **NoSQL Injection Prevention**
  - Sanitize user input before using in queries
  - Use MongoDB $eq operator for equality checks
  - Disable JavaScript execution where possible

- [ ] **XSS Prevention**
  - Sanitize user input before rendering
  - Use Content Security Policy (CSP) headers
  - Encode output in HTML contexts
  - Validate and sanitize file uploads

## Transport Security

- [ ] **HTTPS/TLS**
  - Enforce HTTPS in production
  - Use TLS 1.2 or higher
  - Implement HSTS headers
  - Redirect HTTP to HTTPS
  - Use secure cookies (Secure, SameSite)

- [ ] **CORS Configuration**
  - Specify exact origins, not wildcards
  - Restrict allowed methods
  - Limit exposed headers
  - Validate preflight requests
  - Never use `*` in production

## Rate Limiting & Abuse Prevention

- [ ] **Rate Limiting**
  - Implement per-IP rate limiting
  - Stricter limits for auth endpoints
  - Use Redis for distributed rate limiting
  - Return 429 status with Retry-After header
  - Different limits for authenticated vs anonymous

- [ ] **Brute Force Protection**
  - Account lockout after failed attempts
  - CAPTCHA after repeated failures
  - Exponential backoff for retries
  - Notify users of suspicious activity

## Data Protection

- [ ] **Sensitive Data**
  - Never log sensitive data (passwords, tokens, PII)
  - Encrypt sensitive data at rest
  - Use environment variables for secrets
  - Implement proper key management
  - Mask sensitive data in logs

- [ ] **API Response Security**
  - Don't expose stack traces in production
  - Remove sensitive fields from responses
  - Implement consistent error messages
  - Use generic error messages for auth failures
  - Include security headers in all responses

## Security Headers

- [ ] **Essential Headers**
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY` or `SAMEORIGIN`
  - `X-XSS-Protection: 1; mode=block` (legacy browsers)
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
  - `Content-Security-Policy` with appropriate directives
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy` for feature restrictions

## File Upload Security

- [ ] **Upload Validation**
  - Validate file types (whitelist, not blacklist)
  - Limit file sizes
  - Scan uploads for malware
  - Store uploads outside web root
  - Rename files to prevent execution
  - Use separate domain for user content

## Dependency Security

- [ ] **Supply Chain**
  - Audit dependencies regularly (`npm audit`)
  - Use lockfiles for reproducible builds
  - Keep dependencies updated
  - Use tools like Snyk or Dependabot
  - Pin dependency versions in production
  - Review dependency licenses

## Logging & Monitoring

- [ ] **Security Logging**
  - Log authentication attempts (success/failure)
  - Log authorization failures
  - Log rate limit violations
  - Log suspicious patterns
  - Use structured logging (JSON)
  - Centralize logs for analysis

- [ ] **Monitoring & Alerting**
  - Monitor for unusual traffic patterns
  - Set up alerts for security events
  - Monitor failed login attempts
  - Track rate limiting triggers
  - Use SIEM for advanced detection

## API Design Security

- [ ] **Versioning**
  - Version your API (/v1/, /v2/)
  - Deprecate old versions gracefully
  - Document breaking changes
  - Maintain backward compatibility when possible

- [ ] **Error Handling**
  - Don't expose internal details
  - Use generic messages for auth errors
  - Log detailed errors server-side
  - Return appropriate HTTP status codes
  - Implement global error handler

## Infrastructure Security

- [ ] **Network Security**
  - Use VPC/network segmentation
  - Restrict database access
  - Use security groups/firewalls
  - Disable unused services/ports
  - Implement DDoS protection

- [ ] **Container Security (if applicable)**
  - Run as non-root user
  - Use minimal base images
  - Scan images for vulnerabilities
  - Use read-only filesystems where possible
  - Don't embed secrets in images

## Testing

- [ ] **Security Testing**
  - Write tests for authentication flows
  - Test authorization rules
  - Test input validation
  - Include security in integration tests
  - Perform regular penetration testing
  - Use automated security scanning tools
