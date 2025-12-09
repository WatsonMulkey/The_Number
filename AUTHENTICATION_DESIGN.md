# Authentication & User Privacy Design

## Executive Summary

Design for secure, privacy-focused authentication that separates user identity from financial data while enabling future features like email/SMS notifications for "The Number."

## Core Principles

1. **Privacy First**: Financial data never linked to identifying information
2. **Zero-Knowledge**: Server cannot see user's budget/spending data
3. **Data Separation**: Identity database separate from budget database
4. **Minimal Data**: Only collect what's absolutely necessary
5. **User Control**: Easy data deletion and export

---

## Threat Model

### What We're Protecting Against:

1. **Data Breach**: Server compromised → attacker gets user data
2. **Insider Threat**: Admin/employee accessing user budgets
3. **Correlation Attack**: Linking email/phone to financial habits
4. **Subpoena/Legal Request**: Government requesting user financial data
5. **Marketing/Analytics**: Third parties profiling users

### What We Accept:

1. User must trust the app on their device
2. Email/SMS providers see delivery info (not content)
3. Basic metadata (signup date, last login) is stored
4. Device security is user's responsibility

---

## Architecture: Two-Database Model

### Database 1: Identity DB (Server/Cloud)
**Purpose**: Authentication, notifications, account management
**Location**: Server (managed by us)
**Contains**:
- User ID (UUID, random)
- Email address (hashed for lookup)
- Phone number (hashed for lookup)
- Password hash (Argon2id)
- Notification preferences
- Account created/last login timestamps
- Email/phone verification status

**Does NOT contain**:
- Budget amounts
- Expense data
- Transaction history
- Income information
- ANY financial data

### Database 2: Budget DB (Local/Encrypted)
**Purpose**: All financial data
**Location**: User's device only
**Contains**:
- All budget data
- Expenses
- Transactions
- Income
- "The Number" calculations

**Encryption**:
- Key derived from user password (PBKDF2)
- Never sent to server
- Local only

---

## Authentication Flow

### 1. Registration

```
User enters:
  - Email or Phone
  - Password (8+ chars, validated locally)

Client side:
  1. Derive encryption key from password (PBKDF2, 100k iterations)
  2. Hash email/phone with SHA-256 for lookup
  3. Hash password with Argon2id for storage
  4. Generate random User ID (UUID v4)
  5. Create encrypted budget database with encryption key

  Send to server:
    - User ID
    - Email hash (for lookup)
    - Phone hash (for lookup)
    - Password hash (Argon2id)
    - Email (encrypted with server public key)
    - Phone (encrypted with server public key)

  DO NOT send:
    - Raw password
    - Encryption key
    - Any budget data

Server side:
  1. Validate password hash format
  2. Store in Identity DB
  3. Send verification email/SMS
  4. Return success + JWT token

Client side:
  1. Store JWT token (short-lived, 15 min)
  2. Store refresh token (longer-lived, 30 days)
  3. Keep budget DB local
```

### 2. Login

```
User enters:
  - Email or Phone
  - Password

Client side:
  1. Hash email/phone for lookup
  2. Request challenge from server

Server responds:
  - Challenge (random nonce)
  - Salt for this user

Client side:
  1. Hash password with Argon2id + salt
  2. Sign challenge with password hash
  3. Send signed challenge + email/phone hash

Server validates:
  1. Lookup user by email/phone hash
  2. Verify challenge signature
  3. Return JWT + refresh token

Client side:
  1. Derive encryption key from password
  2. Unlock local budget database
  3. Store tokens
```

### 3. Daily "Number" Delivery

```
Server (scheduled task):
  1. Query Identity DB for users with daily notification enabled
  2. For each user:
     - Send wake-up request to user's device

User's device (receives wake-up):
  1. Calculate "The Number" locally
  2. Encrypt "The Number" with server's public key
  3. Send encrypted number + User ID to server

Server:
  1. Look up user's email/phone (encrypted)
  2. Decrypt email/phone with private key
  3. Send notification: "Your number today: $XX.XX"
  4. Delete decrypted contact info from memory
  5. DO NOT log the number or contact info together
```

---

## Data Separation Strategy

### Identity Database Schema

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email_hash VARCHAR(64) UNIQUE,      -- SHA-256 of email
    phone_hash VARCHAR(64) UNIQUE,      -- SHA-256 of phone
    email_encrypted TEXT,                -- Encrypted with server key
    phone_encrypted TEXT,                -- Encrypted with server key
    password_hash TEXT NOT NULL,         -- Argon2id
    created_at TIMESTAMP,
    last_login TIMESTAMP,
    verified BOOLEAN DEFAULT FALSE,
    notification_enabled BOOLEAN DEFAULT FALSE,
    notification_time TIME DEFAULT '08:00:00'
);

CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    jwt_token_hash VARCHAR(64),
    created_at TIMESTAMP,
    expires_at TIMESTAMP,
    device_fingerprint TEXT
);

-- NO financial data in this database
-- NO linking between user identity and budget amounts
```

### Budget Database Schema (Local)

```sql
-- Same as current schema, but add:
CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT
);

INSERT INTO metadata VALUES
    ('user_id', 'uuid-goes-here'),      -- Links to Identity DB
    ('encrypted_with', 'password-derived-key'),
    ('version', '1.0');

-- All existing tables (settings, expenses, transactions)
-- Encrypted at rest with user's password-derived key
```

### Separation Enforcement

**Identity DB can see:**
- Email/phone (encrypted)
- Login times
- Notification preferences
- Device info

**Identity DB CANNOT see:**
- Budget amounts
- Income
- Expenses
- Transactions
- "The Number"

**Budget DB contains:**
- All financial data
- User ID (for linking)

**Budget DB is:**
- Local only
- Never transmitted
- Encrypted with password-derived key
- Server never sees it

---

## Privacy-Preserving "Number" Delivery

### Option 1: Client-Initiated (Most Private)

```
User's device (scheduled daily):
  1. Calculate "The Number"
  2. Authenticate to server
  3. Request: "Send notification to my email/phone"
  4. Server looks up contact info
  5. Server sends: "Your number: $XX.XX"

Privacy: Server never stores the number
```

### Option 2: Server-Initiated with Encryption

```
Server (scheduled daily):
  1. Send wake-up ping to user

User's device:
  1. Calculate "The Number"
  2. Encrypt with server's public key
  3. Send encrypted number to server

Server:
  1. Decrypt number (in memory only)
  2. Send notification immediately
  3. Zero out decrypted value
  4. Never log the number

Privacy: Server sees number temporarily, not stored
```

### Option 3: Zero-Knowledge (Most Complex)

```
User's device:
  1. Calculate "The Number"
  2. Encrypt with user's public key
  3. Send encrypted number + commitment to server

Server:
  1. Forward encrypted number to email/SMS
  2. User receives encrypted message
  3. User decrypts on their device

Privacy: Server never sees the number at all
Downside: Requires client-side decryption of email/SMS
```

**Recommendation**: Start with Option 1 (client-initiated), consider Option 2 for better UX

---

## Security Measures

### Password Security

1. **Client-side**:
   - Min 8 characters
   - Strength meter
   - PBKDF2 for key derivation (100k iterations)
   - Never sent to server

2. **Server-side**:
   - Argon2id for password hashing
   - Unique salt per user
   - Rate limiting (5 attempts/hour)
   - Account lockout after 10 failed attempts

### Encryption Keys

1. **Budget Encryption Key**:
   - Derived from password using PBKDF2
   - 256-bit AES key
   - Never leaves device
   - Re-derived on each login

2. **Server Keys** (for contact info encryption):
   - RSA 4096-bit keypair
   - Private key in HSM (Hardware Security Module)
   - Public key shared with clients
   - Rotate every 90 days

3. **Transport**:
   - TLS 1.3 only
   - Certificate pinning
   - Perfect forward secrecy

### Token Security

1. **JWT Access Token**:
   - Short-lived (15 minutes)
   - Contains: user_id, issued_at, expires_at
   - Does NOT contain: email, phone, financial data
   - Signed with server secret (HS256)

2. **Refresh Token**:
   - Longer-lived (30 days)
   - Stored hashed in database
   - One-time use (rotation)
   - Device-bound

### Rate Limiting

```
Endpoint                    Limit
---------------------------------
POST /auth/register         3/hour per IP
POST /auth/login           5/hour per email
POST /auth/verify-email    3/hour per email
POST /notifications/send   10/day per user
```

---

## Privacy Features

### 1. Minimal Data Collection

**We collect**:
- Email OR phone (user choice)
- Password hash
- Account creation date
- Last login timestamp
- Notification preferences

**We DON'T collect**:
- Name
- Address
- Payment info (app is free)
- IP addresses (logged temporarily, deleted after 7 days)
- Device details (only generic fingerprint for sessions)
- Analytics/tracking
- Third-party integrations

### 2. Data Anonymization

- User ID is random UUID (not sequential)
- Email/phone hashed for lookups
- Financial data never transmitted to server
- No correlation between identity and budget

### 3. Right to Deletion

```
User requests account deletion:
  1. Server deletes from Identity DB
  2. User keeps local budget DB
  3. User can export budget data first
  4. 30-day grace period before permanent deletion
  5. Notification preferences immediately disabled
```

### 4. Data Export

```
User requests data export:
  - Identity info (email, phone, preferences) → JSON
  - Budget data (already local) → CSV export
  - No server-side financial data to export
```

### 5. Transparency

- Open source client code
- Published security audit (before launch)
- Privacy policy in plain language
- No hidden data collection
- No third-party analytics

---

## Regulatory Compliance

### GDPR (EU)

✅ Right to access (export)
✅ Right to deletion
✅ Right to rectification (user can update)
✅ Data minimization (only collect necessary data)
✅ Purpose limitation (only for notifications)
✅ Storage limitation (local budget data)
✅ Encryption (at rest and in transit)

### CCPA (California)

✅ Right to know (transparency)
✅ Right to delete
✅ Right to opt-out (notifications optional)
✅ No sale of data (we don't sell anything)

### COPPA (Children's Privacy)

⚠️ Age verification (13+)
⚠️ Parental consent if under 13
**Recommendation**: Require users to be 18+ to avoid complexity

---

## Implementation Phases

### Phase 1: Local-Only (Current State)
- ✅ No authentication
- ✅ Local encrypted database
- ✅ No server

### Phase 2: Optional Cloud Backup
- Add authentication (email/password)
- Encrypted backup to server
- User can restore on new device
- Still works offline

### Phase 3: Notifications
- User opts in to daily "Number" delivery
- Client-initiated (device calculates and sends)
- Email or SMS (user choice)

### Phase 4: Multi-Device Sync
- Sync encrypted budget across devices
- End-to-end encrypted
- Server can't decrypt

---

## Technology Stack

### Client (App)
```python
# Authentication
- cryptography (Fernet, PBKDF2)
- pyjwt (JWT tokens)
- argon2-cffi (password hashing)

# Database
- sqlcipher (encrypted SQLite)
- Current encrypted DB implementation
```

### Server (Future)
```python
# Framework
- FastAPI (async, modern)
- uvicorn (ASGI server)

# Database
- PostgreSQL (Identity DB)
- SQLAlchemy (ORM)

# Security
- cryptography (encryption)
- argon2-cffi (password hashing)
- python-jose (JWT)

# Notifications
- SendGrid (email)
- Twilio (SMS)

# Infrastructure
- Docker containers
- AWS/GCP with encryption at rest
- Cloudflare (DDoS protection)
```

---

## Attack Scenarios & Mitigations

### Scenario 1: Server Breach

**What attacker gets**:
- Encrypted email/phone numbers
- Password hashes (Argon2id)
- User IDs
- Login timestamps

**What attacker DOESN'T get**:
- Budget data (local only)
- Plain-text passwords
- Plain-text contact info (encrypted)
- "The Number" or any financial data

**Mitigation**:
- Notify all users immediately
- Force password reset
- Audit access logs
- Investigate breach

### Scenario 2: Man-in-the-Middle

**Attack**: Intercept communication between app and server

**Mitigation**:
- TLS 1.3 with certificate pinning
- Perfect forward secrecy
- Mutual authentication
- No sensitive data in transit anyway (financial data never sent)

### Scenario 3: Phishing

**Attack**: Fake app steals credentials

**Mitigation**:
- Code signing on distributed app
- Checksum verification
- Warning on unofficial sources
- 2FA option (TOTP)

### Scenario 4: Local Device Compromise

**Attack**: Malware on user's device

**Mitigation**:
- Budget DB encrypted at rest
- Key derived from password (not stored)
- Require password to unlock
- Auto-lock after inactivity
- This is the weakest point (we rely on OS security)

### Scenario 5: Insider Threat

**Attack**: Admin/employee tries to access user budgets

**Mitigation**:
- Budget data not on server (impossible)
- Server only has encrypted contact info
- Audit logs for all admin access
- Principle of least privilege
- Regular security reviews

---

## Code Example: Password-Derived Key

```python
# src/auth.py

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
import base64
import os

def derive_encryption_key(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """
    Derive encryption key from user password.

    Args:
        password: User's password
        salt: Salt (generated if None)

    Returns:
        Tuple of (encryption_key, salt)
    """
    if salt is None:
        salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,  # OWASP recommendation
    )

    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt


def encrypt_budget_db(password: str, db_path: str):
    """
    Encrypt budget database with password-derived key.
    """
    key, salt = derive_encryption_key(password)

    # Store salt in metadata (not secret)
    # Use key for Fernet encryption
    cipher = Fernet(key)

    # Encrypt all sensitive data in DB
    # (Implementation similar to current EncryptedDatabase class)

    return salt


def unlock_budget_db(password: str, salt: bytes, db_path: str):
    """
    Unlock budget database with password.
    """
    key, _ = derive_encryption_key(password, salt)
    cipher = Fernet(key)

    # Try to decrypt a test value
    try:
        # If this succeeds, password is correct
        test_decrypt = cipher.decrypt(stored_test_value)
        return True
    except:
        return False  # Wrong password
```

---

## Recommendations

### Immediate (Before Launch)

1. ✅ Keep app local-only initially
2. ✅ Document authentication plan (this document)
3. ⬜ Security audit by third party
4. ⬜ Privacy policy in plain language
5. ⬜ Terms of service
6. ⬜ Age verification (18+)

### Short-term (v2.0)

1. ⬜ Implement authentication system
2. ⬜ Add encrypted cloud backup (optional)
3. ⬜ Email/SMS notification opt-in
4. ⬜ Open source client code
5. ⬜ Penetration testing

### Medium-term (v3.0)

1. ⬜ Multi-device sync
2. ⬜ 2FA/TOTP option
3. ⬜ Biometric unlock (fingerprint/face)
4. ⬜ Password recovery (with trade-offs)
5. ⬜ SOC 2 compliance

### Long-term (v4.0+)

1. ⬜ End-to-end encrypted sharing (family budgets)
2. ⬜ Zero-knowledge architecture proof
3. ⬜ Decentralized identity option
4. ⬜ Hardware key support (YubiKey)

---

## Privacy-First Alternatives

If we want MAXIMUM privacy, consider:

### Option A: No Server At All
- App stays local forever
- Export "number" to calendar/reminders
- User sets up their own notifications
- No authentication needed
- Zero server cost
- Ultimate privacy

### Option B: Self-Hosted Server
- Users run their own server
- We provide Docker image
- Open source server code
- Users control their data
- We provide hosted option for convenience

### Option C: Peer-to-Peer
- Devices sync directly (no server)
- Use local network or Bluetooth
- IPFS for backup storage
- Maximum decentralization
- Complex UX

**Recommendation**: Start with local-only (Option A), add optional cloud later

---

## Decision Matrix

| Feature | Privacy | UX | Complexity | Cost |
|---------|---------|----|-----------| -----|
| Local-only | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | $0 |
| Cloud backup | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | $$ |
| Notifications | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | $$$ |
| Multi-device sync | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $$$$ |

---

## Conclusion

**Recommended Approach**:

1. **Now**: Stay local-only (maximum privacy, zero cost)
2. **v2.0**: Add optional authentication + notifications
3. **Architecture**: Two-database model with data separation
4. **Privacy**: Zero-knowledge where possible, minimal data collection
5. **Security**: Password-derived encryption, Argon2id, TLS 1.3

**Key Insight**: By keeping financial data local and only transmitting the daily "number" when needed, we achieve both privacy and UX. The server only needs to know "send $66.67 to user@email.com" - it never sees the budget, income, or expenses that created that number.

**Trade-off**: If user loses their device AND forgets their password, budget data is unrecoverable. This is the price of true privacy. We should make this clear to users.

---

## Next Steps

1. Review this design with security expert
2. Decide on launch strategy (local-only vs. cloud)
3. Implement Phase 1 if going cloud
4. Draft privacy policy and terms
5. Plan security audit timeline

**Status**: Design complete, awaiting decision on cloud vs. local-only
