from celery import Celery
from app.core.config import settings

# Initialize Celery app
# The broker and backend URLs are pulled from our config.py
celery_app = Celery(
    "trade_copilot_worker",
    broker=settings.redis_url,
    backend=settings.redis_url
)

# Optional Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
