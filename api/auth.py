"""
Authentication utilities for The Number API.

Provides password hashing, JWT token generation, user authentication, and rate limiting.
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
from collections import defaultdict
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY not found in environment variables. "
        "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

# Security
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password for storing."""
    # Bcrypt has a 72 byte limit - truncate if necessary
    # This is safer than rejecting long passwords
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password = password_bytes[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    # Apply same truncation as hash_password to match stored hash
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        plain_password = password_bytes[:72].decode('utf-8', errors='ignore')
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """
    Dependency to get the current user ID from JWT token.

    Usage:
        @app.get("/protected")
        async def protected_route(user_id: int = Depends(get_current_user_id)):
            return {"user_id": user_id}
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id: int = payload.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


# ============================================================================
# PASSWORD RESET
# ============================================================================

# Simple in-memory password reset token storage (use Redis for production)
# Format: {token: {username: str, expires: datetime}}
_reset_tokens: Dict[str, dict] = {}

def generate_reset_token(username: str) -> str:
    """
    Generate a password reset token for a user.

    Args:
        username: The username requesting password reset

    Returns:
        A secure random token string
    """
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour

    _reset_tokens[token] = {
        "username": username,
        "expires": expires
    }

    return token


def verify_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token and return the username if valid.

    Args:
        token: The reset token to verify

    Returns:
        Username if token is valid, None otherwise
    """
    if token not in _reset_tokens:
        return None

    token_data = _reset_tokens[token]

    # Check if token has expired
    if datetime.utcnow() > token_data["expires"]:
        # Clean up expired token
        del _reset_tokens[token]
        return None

    return token_data["username"]


def invalidate_reset_token(token: str) -> None:
    """
    Invalidate a reset token after it's been used.

    Args:
        token: The reset token to invalidate
    """
    if token in _reset_tokens:
        del _reset_tokens[token]


# ============================================================================
# RATE LIMITING
# ============================================================================

# Simple in-memory rate limiter (use Redis for production)
_rate_limit_cache: Dict[str, list] = defaultdict(list)

def check_rate_limit(
    request: Request,
    max_requests: int = 5,
    window_seconds: int = 60
) -> None:
    """
    Simple rate limiting check.

    Args:
        request: FastAPI request object
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds

    Raises:
        HTTPException: If rate limit is exceeded
    """
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"

    # Clean up old entries
    now = datetime.utcnow()
    cutoff = now - timedelta(seconds=window_seconds)

    # Remove expired entries
    _rate_limit_cache[client_ip] = [
        timestamp for timestamp in _rate_limit_cache[client_ip]
        if timestamp > cutoff
    ]

    # Check if limit exceeded
    if len(_rate_limit_cache[client_ip]) >= max_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {window_seconds} seconds."
        )

    # Add current request
    _rate_limit_cache[client_ip].append(now)
