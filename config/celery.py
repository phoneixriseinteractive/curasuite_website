"""
CuraSuite — Celery Configuration
Background task processing for emails, publishing, AI tasks, image optimization, etc.
"""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("curasuite")

# Read config from Django settings, using CELERY_ prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self) -> None:
    """Debug task — prints request info. Remove before production."""
    print(f"Request: {self.request!r}")
