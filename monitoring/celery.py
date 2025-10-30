import os
from celery import Celery
from celery.schedules import crontab

app = Celery('monitoring')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://redis_cache:6379/0')
app.conf.result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis_cache:6379/0')

app.conf.beat_schedule = {
    'send-daily-api-report': {
        'task': 'dashboard.tasks.send_daily_api_report',
        'schedule': crontab(hour=9, minute=00),  # Tous les jours à 9h20
    },
}
