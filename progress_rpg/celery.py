from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'progress_rpg.settings')

app = Celery('progress_rpg')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

app.conf.beat_schedule = {
    'update-quests-every-hour': {
        'task': 'progress_rpg.tasks.update_quest_availability',
        'schedule': crontab(minute=0, hour='*'), # Run every hour
    },
}
