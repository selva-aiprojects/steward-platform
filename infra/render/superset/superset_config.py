import os

# Render injects connection URLs through env vars.
# Support both SQLALCHEMY_DATABASE_URI and DATABASE_URL for consistency
# with backend service conventions.
SQLALCHEMY_DATABASE_URI = os.getenv(
    "SQLALCHEMY_DATABASE_URI",
    os.getenv("DATABASE_URL", "sqlite:////app/superset_home/superset.db"),
)

SECRET_KEY = os.getenv("SUPERSET_SECRET_KEY", "unsafe-dev-key-change-me")

FEATURE_FLAGS = {
    "ALERT_REPORTS": True,
}

# Robust cache configuration
REDIS_URL = os.getenv("REDIS_URL")
if REDIS_URL:
    CACHE_CONFIG = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_REDIS_URL": REDIS_URL,
        "CACHE_DEFAULT_TIMEOUT": 300,
    }
    DATA_CACHE_CONFIG = CACHE_CONFIG
    RESULTS_BACKEND = CACHE_CONFIG
else:
    CACHE_CONFIG = {
        "CACHE_TYPE": "SimpleCache",
        "CACHE_DEFAULT_TIMEOUT": 300,
    }
    DATA_CACHE_CONFIG = CACHE_CONFIG
    RESULTS_BACKEND = None # Disable results backend if no Redis

WTF_CSRF_ENABLED = False
TALISMAN_ENABLED = False

# Embed-friendly settings for local admin portal integration.
ENABLE_CORS = True
CORS_OPTIONS = {
    "supports_credentials": True,
    "origins": [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
}

SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = False
X_FRAME_OPTIONS = "ALLOWALL"

# Public access for embedding
PUBLIC_ROLE_LIKE = "Gamma"
PUBLIC_ROLE_LIKE_GAMMA = True
AUTH_ROLE_PUBLIC = "Public"
