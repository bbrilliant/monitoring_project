# monitoring_project/__init__.py
from __future__ import absolute_import, unicode_literals

# Importer Celery dès que Django démarre
from .celery import app as celery_app

__all__ = ('celery_app',)
