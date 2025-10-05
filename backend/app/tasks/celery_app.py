# app/tasks/celery_app.py
from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()

# Initialize Celery
celery_app = Celery(
    "crypto_portfolio",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.tasks.portfolio_tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_prefetch_multiplier=1,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    'update-all-portfolios-every-15-minutes': {
        'task': 'app.tasks.portfolio_tasks.update_all_portfolio_values',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'update-coin-prices-every-5-minutes': {
        'task': 'app.tasks.portfolio_tasks.update_coin_prices_cache',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
}
