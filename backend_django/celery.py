# django_celery/celery.py

import os
from celery import Celery

from apps.cripto_info.tasks import MyCache

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend_django.settings")
app = Celery("backend_django")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')



