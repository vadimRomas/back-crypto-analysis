from .celery import app as celery_app

__all__ = ("celery_app",)


# import os
# from celery import Celery
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend_django.settings")
# app = Celery("backend_django")
# app.config_from_object("django.conf:settings", namespace="CELERY")
# app.autodiscover_tasks()


# @celery_app.task(bind=True)
# def app_celery():
#     print('op')
