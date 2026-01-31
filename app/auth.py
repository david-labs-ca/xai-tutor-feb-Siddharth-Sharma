"""
Authentication utilities: JWT creation/verification and password hashing.
"""

import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# bcrypt has a 72-byte limit; we pre-hash with SHA256 so long passwords work.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


def _password_digest(password: str) -> str:
    """SHA256 digest of password (UTF-8). Keeps input to bcrypt under 72 bytes."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    """Hash a plain password (any length; pre-hashed before bcrypt)."""
    return pwd_context.hash(_password_digest(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hash. Supports both new (SHA256+bcrypt) and legacy (bcrypt-only) hashes."""
    digest = _password_digest(plain_password)
    if pwd_context.verify(digest, hashed_password):
        return True
    # Legacy: password was stored as bcrypt(plain) for passwords <= 72 bytes
    if len(plain_password.encode("utf-8")) <= 72:
        return pwd_context.verify(plain_password, hashed_password)
    return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token. Returns payload or None."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> int:
    """
    Dependency: extract user_id from JWT Bearer token.
    Use this on routes that require authentication.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user in token",
            headers={"WWW-Authenticate": "Bearer"},
        )
