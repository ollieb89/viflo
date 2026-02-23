# Example: Authentication Phase

This example shows a complete authentication phase with 2 plans.

## Phase Context

```markdown
# Phase 1 Context: Authentication

## Visual Design

### Login Page
- Clean, minimal design
- Centered card layout
- Dark mode support

### Forms
- Floating labels
- Inline validation
- Password visibility toggle

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Auth method | JWT + httpOnly cookies | Secure, scalable |
| Password hashing | bcrypt (10 rounds) | Industry standard |
| Email verification | Required | Security |
| OAuth providers | Google, GitHub | Common user preferences |
```

## Plan 1: Database & Models

```xml
<plan phase="1" plan="1">
  <overview>
    <phase_name>Authentication - Database & Models</phase_name>
    <goal>Create user model and authentication tables</goal>
  </overview>
  
  <tasks>
    <task type="auto" priority="1">
      <name>Create User model</name>
      <files>prisma/schema.prisma</files>
      <action>
Add User model with:
- id (cuid)
- email (unique, indexed)
- password_hash (nullable for OAuth users)
- email_verified (datetime, nullable)
- created_at, updated_at
- oauth_provider, oauth_id (for OAuth)
      </action>
      <verify>npx prisma validate passes</verify>
      <done>User model exists with all fields</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create RefreshToken model</name>
      <files>prisma/schema.prisma</files>
      <action>
Add RefreshToken model with:
- id (cuid)
- token_hash (indexed for lookup)
- user_id (foreign key)
- expires_at
- created_at
- revoked_at (nullable)
      </action>
      <verify>Relations to User model correct</verify>
      <done>RefreshToken model exists</done>
    </task>
    
    <task type="manual" priority="1">
      <name>Run database migration</name>
      <action>Run: npx prisma migrate dev --name add_auth_models</action>
      <verify>Migration file created in prisma/migrations/</verify>
    </task>
    
    <task type="auto" priority="2">
      <name>Generate Prisma client</name>
      <files>src/lib/db.ts</files>
      <action>Run: npx prisma generate</action>
      <verify>Types updated in node_modules/.prisma/client</verify>
      <done>Prisma client has User and RefreshToken types</done>
    </task>
  </tasks>
</plan>
```

## Plan 2: API Routes & Frontend

```xml
<plan phase="1" plan="2">
  <overview>
    <phase_name>Authentication - API & UI</phase_name>
    <goal>Implement login/signup endpoints and login page</goal>
  </overview>
  
  <dependencies>
    <complete>Plan 1: Database & Models</complete>
  </dependencies>
  
  <tasks>
    <task type="auto" priority="1">
      <name>Create auth utilities</name>
      <files>src/lib/auth.ts</files>
      <action>
Create auth utilities:
- hashPassword(password): returns bcrypt hash
- verifyPassword(password, hash): returns boolean
- createTokens(userId): returns {accessToken, refreshToken}
- verifyAccessToken(token): returns payload
- verifyRefreshToken(tokenHash): returns user
- setAuthCookies(res, tokens): sets httpOnly cookies
      </action>
      <verify>Unit tests pass for all functions</verify>
      <done>All auth utilities implemented and tested</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create register API route</name>
      <files>src/app/api/auth/register/route.ts</files>
      <action>
Create POST /api/auth/register:
- Validate email format
- Check email not already used
- Hash password with bcrypt
- Create user record
- Return 201 with user (no password)
- Return 400 for validation errors
- Return 409 for duplicate email
      </action>
      <verify>
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
Returns 201
      </verify>
      <done>Registration endpoint works</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create login API route</name>
      <files>src/app/api/auth/login/route.ts</files>
      <action>
Create POST /api/auth/login:
- Validate email and password present
- Find user by email
- Verify password matches hash
- Create access and refresh tokens
- Set httpOnly cookies
- Return 200 with user
- Return 401 for invalid credentials
      </action>
      <verify>
Login returns 200 + Set-Cookie headers
Invalid credentials return 401
      </verify>
      <done>Login endpoint works with cookie auth</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create login page</name>
      <files>src/app/login/page.tsx, src/components/auth/LoginForm.tsx</files>
      <action>
Create login page:
- Email input with validation
- Password input with visibility toggle
- Submit button with loading state
- Link to register page
- Error message display
- Call /api/auth/login on submit
- Redirect to dashboard on success
      </action>
      <verify>Can log in through UI, redirects after success</verify>
      <done>Login page functional</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create register page</name>
      <files>src/app/register/page.tsx, src/components/auth/RegisterForm.tsx</files>
      <action>
Create register page:
- Email input with validation
- Password input with strength indicator
- Confirm password input
- Submit button with loading state
- Link to login page
- Call /api/auth/register on submit
- Show success message, offer to login
      </action>
      <verify>Can register through UI</verify>
      <done>Register page functional</done>
    </task>
  </tasks>
</plan>
```

## Verification

| Check | Status |
|-------|--------|
| User can register | ✅ |
| User can login | ✅ |
| Passwords are hashed | ✅ |
| JWT tokens in httpOnly cookies | ✅ |
| Validation errors show inline | ✅ |
| Responsive design | ✅ |
| Dark mode support | ✅ |
