# backend/app/core/database.py
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

logger = logging.getLogger(__name__)

# Build connection arguments (SSL for Supabase/production)
_connect_args = {}
if os.getenv("DATABASE_SSL", "false").lower() in ("true", "1", "yes"):
    import ssl
    ssl_context = ssl.create_default_context()
    ca_path = os.getenv("DATABASE_SSL_CA", "")
    if ca_path:
        ssl_context.load_verify_locations(ca_path)
    else:
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
    _connect_args["ssl"] = ssl_context
    logger.info("[DB] SSL enabled for database connection")

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # Detect stale connections
    pool_size=5,              # Concurrent connections in the pool
    max_overflow=10,          # Extra connections under burst load
    pool_timeout=30,          # Seconds to wait for a connection
    pool_recycle=1800,        # Recycle connections every 30 min
    connect_args=_connect_args,
    echo=False,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database error in get_db(): {e}")
        raise
    finally:
        db.close()
