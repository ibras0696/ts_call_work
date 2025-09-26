from __future__ import annotations
from celery import Celery
from .config import settings

celery_app = Celery(
    "calls_service",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Basic Celery settings
celery_app.conf.task_acks_late = True
celery_app.conf.worker_prefetch_multiplier = 1
celery_app.conf.task_track_started = True

# Autodiscover tasks inside app package
celery_app.autodiscover_tasks(["app"])
