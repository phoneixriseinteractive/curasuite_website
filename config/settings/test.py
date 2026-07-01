from .base import *
SECRET_KEY = "test-secret-key-curasuite-not-for-production"
DEBUG = True
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
SESSION_ENGINE = "django.contrib.sessions.backends.db"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
