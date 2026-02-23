# Phase {N} Context: API/Backend Feature

## API Design

### Endpoints
- [ ] RESTful or RPC style
- [ ] URL structure / versioning
- [ ] HTTP methods (GET, POST, PUT, DELETE, PATCH)

### Request Format
- [ ] Content-Type (JSON, form-data)
- [ ] Required vs optional fields
- [ ] Validation rules

### Response Format
- [ ] Success response structure
- [ ] Error response structure
- [ ] Status codes to use

## Error Handling

### Error Categories
- [ ] Validation errors (400)
- [ ] Authentication errors (401)
- [ ] Authorization errors (403)
- [ ] Not found errors (404)
- [ ] Server errors (500)

### Error Response Format
```json
{
  "error": "",
  "code": "",
  "details": {}
}
```

## Authentication

- [ ] Auth method (JWT, API key, session)
- [ ] Token location (header, cookie)
- [ ] Token expiration

## Rate Limiting

- [ ] Limits per endpoint
- [ ] Rate limit headers

## Pagination

- [ ] Cursor or offset-based
- [ ] Default page size
- [ ] Max page size

## Caching

- [ ] Cache headers (ETag, Cache-Control)
- [ ] Cache duration

## Decisions Log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| {Decision} | {Choice} | {Why} |
