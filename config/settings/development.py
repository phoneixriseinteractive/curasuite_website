"""
CuraSuite — Development Settings
Local development overrides. Never use in production.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from .base import *  # noqa: F401, F403

# Load .env file from project root
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

# ── Core ───────────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-dev-only-change-this-in-production-curasuite-2025",
)
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "[::1]"]


# ── Database ───────────────────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "curasuite_dev"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "Neha@0364"),
        "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        "OPTIONS": {
            "connect_timeout": 10,
        },
        "CONN_MAX_AGE": 0,  # Disable persistent connections in dev
    }
}


# ── Cache (dev — use Redis if available, fallback to LocMem) ───────────────────
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "curasuite-dev",
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.db"


# ── Email ──────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# ── Static & Media ─────────────────────────────────────────────────────────────
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"


# ── Debug Toolbar (install django-debug-toolbar separately) ───────────────────
# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
# INTERNAL_IPS = ["127.0.0.1"]


# ── Dev-friendly security settings ────────────────────────────────────────────
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
