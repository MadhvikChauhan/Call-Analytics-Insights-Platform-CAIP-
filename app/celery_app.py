
"""Celery application configuration for background tasks."""
from celery import Celery
from config import settings

celery = Celery(
    "caip",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)
# Route tasks to queues to allow separation of worker types
celery.conf.task_routes = {
    'app.tasks.process_call_record': {'queue': 'calls'},
    'app.tasks.generate_company_report': {'queue': 'reports'}
}
