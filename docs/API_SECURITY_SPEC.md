# API Security Specification
**Project:** The Number - PWA Backend API
**Date:** 2025-12-15
**Status:** Draft for Review

---

## Overview

This document specifies the security requirements and implementation for The Number PWA backend API built with FastAPI.

---

## 1. Authentication & Authorization

### JWT Token Strategy

**Access Tokens:**
- Algorithm: HS256 (HMAC with SHA-256)
- Secret: 256-bit random key (stored in environment variable)
- Expiration: 1 hour
- Payload:
  ```json
  {
    "sub": "user_id",
    "email": "user@example.com",
    "exp": 1234567890,
    "iat": 1234567890
  }
  ```

**Refresh Tokens:**
- Stored in httpOnly cookie (not accessible via JavaScript)
- Expiration: 7 days
- Rotated on each use
- Stored in database for revocation capability

**Token Storage:**
- Frontend: Access token in memory (NOT localStorage - XSS risk)
- Refresh token: httpOnly, secure, SameSite=Strict cookie
- On page reload: Use refresh token to get new access token

**Token Validation:**
- Verify signature
- Check expiration
- Verify user still exists and is active
- Check if token is revoked (for refresh tokens)

### Authentication Flow

```
1. POST /api/auth/signup
   - Create user with hashed password (bcrypt, cost=12)
   - Return access + refresh tokens

2. POST /api/auth/login
   - Verify email + password
   - Return access + refresh tokens
   - Rate limited: 5 attempts per 15 minutes per IP

3. POST /api/auth/refresh
   - Verify refresh token from cookie
   - Return new access token + new refresh token
   - Invalidate old refresh token

4. POST /api/auth/logout
   - Revoke refresh token
   - Clear cookie
```

### Password Requirements

- Minimum 8 characters
- At least 1 uppercase, 1 lowercase, 1 number
- No common passwords (check against list of top 10k)
- Hashed with bcrypt (cost factor: 12)
- Never logged or displayed

---

## 2. Rate Limiting

**Per-Endpoint Limits:**

| Endpoint | Limit | Window | Reason |
|----------|-------|--------|--------|
| POST /api/auth/login | 5 requests | 15 min | Prevent brute force |
| POST /api/auth/signup | 3 requests | 1 hour | Prevent spam accounts |
| POST /api/auth/refresh | 10 requests | 1 hour | Normal usage pattern |
| GET /api/budget/* | 100 requests | 1 min | Normal UI polling |
| POST /api/transactions | 30 requests | 1 min | Prevent abuse |
| POST /api/expenses | 30 requests | 1 min | Prevent abuse |
| PUT/DELETE /api/* | 60 requests | 1 min | General modification |

**Implementation:**
- Use `slowapi` library (Redis-backed or in-memory)
- Return HTTP 429 (Too Many Requests) with Retry-After header
- Rate limit by: IP address + user ID (if authenticated)

**Response on Rate Limit:**
```json
{
  "error": "Too many requests",
  "message": "Please wait 60 seconds before trying again",
  "retry_after": 60
}
```

---

## 3. CORS Configuration

**Allowed Origins:**
- Development: `http://localhost:4321`, `http://localhost:3000`
- Production: `https://thenumber.app` (and www subdomain)

**Configuration:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4321",  # Astro dev server
        "https://thenumber.app",
        "https://www.thenumber.app"
    ],
    allow_credentials=True,  # For cookies
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600  # Cache preflight for 10 minutes
)
```

**Security Notes:**
- NEVER use `allow_origins=["*"]` with `allow_credentials=True`
- Only allow necessary methods
- Validate Origin header on every request

---

## 4. Input Validation

### Reuse Existing Validation

**Leverage security constants from calculator.py:**
```python
MAX_STRING_LENGTH = 200
MAX_AMOUNT = 10_000_000
MAX_DAYS_UNTIL_PAYCHECK = 365
```

### Pydantic Models for API

**Example: Transaction Request**
```python
from pydantic import BaseModel, Field, validator

class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0, le=MAX_AMOUNT)
    description: str = Field(..., min_length=1, max_length=MAX_STRING_LENGTH)
    date: Optional[str] = None

    @validator('description')
    def validate_description(cls, v):
        # Strip whitespace
        v = v.strip()
        if not v:
            raise ValueError("Description cannot be empty")
        return v

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        if v > MAX_AMOUNT:
            raise ValueError(f"Amount exceeds maximum (${MAX_AMOUNT:,})")
        return v
```

**Example: Expense Request**
```python
class ExpenseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=MAX_STRING_LENGTH)
    amount: float = Field(..., gt=0, le=MAX_AMOUNT)
    is_fixed: bool

    @validator('name')
    def validate_name(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Expense name cannot be empty")
        return v
```

### Validation Error Response

```json
{
  "error": "Validation Error",
  "details": [
    {
      "field": "amount",
      "message": "Amount must be positive",
      "value": -10.5
    }
  ]
}
```

---

## 5. SQL Injection Prevention

**Already Implemented:**
- Parameterized queries (sqlite3 placeholders)
- Whitelist validation for column names
- No f-strings in SQL queries

**Verification:**
- All database.py methods use `?` placeholders
- Column names validated against ALLOWED_COLUMNS whitelist

**Example from database.py:**
```python
ALLOWED_COLUMNS = {'name', 'amount', 'is_fixed', 'updated_at'}

# Safe parameterized query
cursor.execute("UPDATE expenses SET name = ?, amount = ? WHERE id = ?",
               (name, amount, expense_id))
```

---

## 6. XSS Prevention

**API Response Sanitization:**
- API returns JSON (Content-Type: application/json)
- Frontend must sanitize before rendering HTML
- Never return HTML from API

**Frontend Responsibility:**
- Astro/React automatically escapes variables in JSX
- Never use `dangerouslySetInnerHTML` with user data
- Never use `eval()` or `Function()` with user input

**Content Security Policy (CSP):**
```http
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'unsafe-inline';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self' https://api.thenumber.app;
```

---

## 7. HTTPS & Secure Headers

**HTTPS Enforcement:**
- All production traffic over HTTPS
- HSTS header: `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- Redirect HTTP to HTTPS

**Security Headers:**
```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

---

## 8. Database Security

### User Isolation

**Database Strategy:**
- Option A (Current): User-specific SQLite files
  - Pro: Complete data isolation
  - Con: Hard to scale, backup complexity

- Option B (Recommended): Single SQLite with user_id foreign key
  - Pro: Easier to manage, better concurrency
  - Con: Must ensure queries filter by user_id

**Recommended: Option B with row-level security**

```python
# ALWAYS filter by user_id from JWT token
def get_user_expenses(user_id: int):
    cursor.execute("SELECT * FROM expenses WHERE user_id = ?", (user_id,))
```

### Encryption

**Data at Rest:**
- Use existing Fernet encryption for sensitive fields
- Or use SQLCipher for full database encryption

**Data in Transit:**
- HTTPS for all API calls
- TLS 1.2+ only

### Backup & Recovery

- Automated daily backups
- Store encrypted backups off-site
- Test restore process monthly

---

## 9. Error Handling

### Error Responses

**Never expose:**
- Stack traces
- Database errors
- File paths
- Internal implementation details

**Generic Error Response:**
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred. Please try again.",
  "request_id": "abc123"
}
```

**Log Internally:**
```python
import logging

logger.error(f"Request {request_id} failed", exc_info=True, extra={
    "user_id": user_id,
    "endpoint": request.url.path,
    "method": request.method
})
```

### Status Codes

| Code | Meaning | When to Use |
|------|---------|-------------|
| 200 | OK | Successful GET/PUT/DELETE |
| 201 | Created | Successful POST |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Valid token, no permission |
| 404 | Not Found | Resource doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected error |

---

## 10. Logging & Monitoring

### What to Log

**✅ Log:**
- Authentication attempts (success/failure)
- Failed authorization checks
- Rate limit violations
- Input validation failures
- API errors (with request ID)

**❌ Never Log:**
- Passwords (even hashed)
- Full JWT tokens
- Encryption keys
- Credit card numbers
- Social security numbers

### Log Format

```python
{
  "timestamp": "2025-12-15T10:30:00Z",
  "level": "ERROR",
  "user_id": 12345,
  "request_id": "abc123",
  "endpoint": "/api/transactions",
  "method": "POST",
  "message": "Validation failed: amount exceeds maximum",
  "ip_address": "192.168.1.1"
}
```

### Monitoring Alerts

**Trigger alerts on:**
- >10 failed login attempts in 5 minutes (potential brute force)
- >100 validation errors in 1 minute (potential attack)
- API error rate >1% of requests
- Response time >5 seconds

---

## 11. Environment Variables

**Required Variables:**
```bash
# .env file (NEVER commit to git)
JWT_SECRET_KEY=<256-bit random hex string>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

DATABASE_ENCRYPTION_KEY=<Fernet key>
DATABASE_URL=sqlite:///./data/thenumber.db

CORS_ORIGINS=http://localhost:4321,https://thenumber.app

# Optional
SENTRY_DSN=<error tracking>
LOG_LEVEL=INFO
ENVIRONMENT=production
```

**Generation:**
```python
# Generate JWT secret
import secrets
print(secrets.token_hex(32))  # 256 bits

# Generate Fernet key
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

---

## 12. Dependency Security

**Requirements:**
```
fastapi[all]>=0.104.0
uvicorn[standard]>=0.24.0
python-jose[cryptography]>=3.3.0  # JWT
passlib[bcrypt]>=1.7.4            # Password hashing
slowapi>=0.1.9                    # Rate limiting
pydantic>=2.5.0                   # Validation
python-multipart>=0.0.6           # Form data
```

**Security Practices:**
- Pin major versions
- Run `pip-audit` to check for vulnerabilities
- Update dependencies monthly
- Subscribe to security advisories

---

## 13. Testing Security

**Automated Security Tests:**

1. **Authentication Tests:**
   - Test JWT signature validation
   - Test expired token rejection
   - Test token without signature
   - Test token from different user

2. **Authorization Tests:**
   - Test user A cannot access user B's data
   - Test unauthenticated access blocked

3. **Input Validation Tests:**
   - Test SQL injection attempts
   - Test XSS payloads
   - Test oversized inputs
   - Test negative numbers

4. **Rate Limiting Tests:**
   - Test rate limit triggers
   - Test rate limit resets

**Example Test:**
```python
def test_user_cannot_access_other_user_data():
    # User A creates expense
    expense_id = create_expense(user_a_token, "Rent", 1500)

    # User B tries to access it
    response = client.get(
        f"/api/expenses/{expense_id}",
        headers={"Authorization": f"Bearer {user_b_token}"}
    )

    assert response.status_code == 403
```

---

## 14. Deployment Security

**Pre-Deployment Checklist:**
- [ ] All secrets in environment variables (not code)
- [ ] HTTPS enabled with valid certificate
- [ ] HSTS header enabled
- [ ] Security headers configured
- [ ] CORS limited to production domain
- [ ] Rate limiting enabled
- [ ] Error messages sanitized (no stack traces)
- [ ] Logging configured (no sensitive data)
- [ ] Database backups automated
- [ ] Dependency vulnerabilities checked
- [ ] Security tests passing

**Railway/Render Configuration:**
- Set environment variables in dashboard
- Enable automatic HTTPS
- Configure custom domain
- Set up health check endpoint: `GET /health`

---

## 15. Incident Response Plan

**If Security Breach Detected:**

1. **Immediate (< 1 hour):**
   - Revoke all refresh tokens (force re-login)
   - Rotate JWT secret key
   - Take affected service offline if necessary

2. **Investigation (< 24 hours):**
   - Review logs for scope of breach
   - Identify affected users
   - Determine attack vector

3. **Communication (< 48 hours):**
   - Notify affected users via email
   - Post incident report publicly
   - Report to authorities if required (GDPR)

4. **Remediation:**
   - Fix vulnerability
   - Add tests to prevent regression
   - Deploy fix
   - Monitor for further attacks

---

## 16. Compliance

**GDPR Considerations:**
- Data minimization: Only collect necessary data
- Right to access: API to export user data
- Right to deletion: API to delete user account
- Data portability: JSON export format
- Privacy policy: Link from signup page

**Implementation:**
```python
# GET /api/users/me/export
# Returns all user data in JSON format

# DELETE /api/users/me
# Permanently deletes user and all associated data
```

---

## Review Checklist

Before implementing, verify:
- [ ] JWT strategy is clear
- [ ] Rate limits are reasonable
- [ ] CORS is locked down
- [ ] All inputs are validated
- [ ] SQL injection is prevented
- [ ] XSS prevention is in place
- [ ] HTTPS is enforced
- [ ] Errors don't leak info
- [ ] Logging excludes sensitive data
- [ ] Environment variables are defined
- [ ] Security tests are planned

**Status:** Ready for implementation
**Next Step:** Review with team, then proceed to API development
