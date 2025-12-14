"""Celery application configuration."""

from celery import Celery

from src.config.settings import settings

# Create Celery app
celery_app = Celery(
    "shop_service",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Scheduled tasks (cron)
celery_app.conf.beat_schedule = {
    "cleanup-expired-orders": {
        "task": "workers.scheduled.periodic_tasks.cleanup_expired_orders",
        "schedule": 86400.0,  # Every day at midnight
    },
    "generate-daily-report": {
        "task": "workers.scheduled.periodic_tasks.generate_daily_report",
        "schedule": 86400.0 + 3600.0,  # Every day at 1:00 AM
    },
}


