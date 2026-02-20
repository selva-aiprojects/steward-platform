import os

# Render injects connection URLs through env vars.
# Support both SQLALCHEMY_DATABASE_URI and DATABASE_URL for consistency
# with backend service conventions.
SQLALCHEMY_DATABASE_URI = os.getenv(
    "SQLALCHEMY_DATABASE_URI",
    os.getenv("DATABASE_URL", "sqlite:////app/superset_home/superset.db"),
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
SECRET_KEY = os.getenv("SUPERSET_SECRET_KEY", "unsafe-dev-key-change-me")

FEATURE_FLAGS = {
    "ALERT_REPORTS": True,
}

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_REDIS_URL": REDIS_URL,
    "CACHE_DEFAULT_TIMEOUT": 300,
}

DATA_CACHE_CONFIG = CACHE_CONFIG
RESULTS_BACKEND = CACHE_CONFIG

WTF_CSRF_ENABLED = True
TALISMAN_ENABLED = False
