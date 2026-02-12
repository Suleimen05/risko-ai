"""
Security utilities for password hashing and JWT token management.
Production-ready with token blacklisting support.
"""
import os
import uuid
import time as _time
import logging
from datetime import datetime, timedelta
from typing import Optional
from collections import OrderedDict

from jose import JWTError, jwt
from passlib.context import CryptContext
from ..core.config import settings

logger = logging.getLogger(__name__)

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


# =============================================================================
# TOKEN BLACKLIST
# =============================================================================

class TokenBlacklist:
    """
    JWT token blacklist using jti claims.
    In-memory with automatic cleanup. Optionally backed by Redis.
    """

    def __init__(self, max_size: int = 10000):
        self._blacklist: OrderedDict[str, float] = OrderedDict()
        self._max_size = max_size
        self._redis = None
        self._redis_checked = False

    def _get_redis(self):
        if self._redis_checked:
            return self._redis
        self._redis_checked = True
        redis_url = os.getenv("REDIS_URL", "")
        if redis_url:
            try:
                import redis
                self._redis = redis.from_url(redis_url, decode_responses=True)
                self._redis.ping()
                logger.info("TokenBlacklist: Using Redis backend")
            except Exception:
                self._redis = None
        return self._redis

    def blacklist(self, jti: str, exp: float) -> None:
        r = self._get_redis()
        if r:
            ttl = max(1, int(exp - _time.time()))
            r.setex(f"bl:{jti}", ttl, "1")
        else:
            self._cleanup()
            self._blacklist[jti] = exp

    def is_blacklisted(self, jti: str) -> bool:
        r = self._get_redis()
        if r:
            return r.exists(f"bl:{jti}") > 0
        return jti in self._blacklist and self._blacklist[jti] > _time.time()

    def _cleanup(self) -> None:
        now = _time.time()
        expired = [k for k, v in self._blacklist.items() if v <= now]
        for k in expired:
            del self._blacklist[k]
        while len(self._blacklist) > self._max_size:
            self._blacklist.popitem(last=False)


token_blacklist = TokenBlacklist()


# =============================================================================
# PASSWORD UTILITIES
# =============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storage."""
    return pwd_context.hash(password)


# =============================================================================
# JWT TOKEN CREATION
# =============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with jti for blacklisting."""
    to_encode = data.copy()
    now = datetime.utcnow()
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode.update({
        "exp": expire,
        "iat": now,
        "jti": str(uuid.uuid4()),
        "type": "access",
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token with longer expiration."""
    to_encode = data.copy()
    now = datetime.utcnow()
    expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": now,
        "jti": str(uuid.uuid4()),
        "type": "refresh",
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token, checking blacklist."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if jti and token_blacklist.is_blacklisted(jti):
            return None
        return payload
    except JWTError:
        return None
