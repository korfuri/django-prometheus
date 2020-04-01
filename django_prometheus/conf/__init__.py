import os

from django.conf import settings

APP_NAME = "django"

if settings.configured:
    APP_NAME = getattr(settings, "METRICS_APP_NAME", APP_NAME)

APP_NAME = os.getenv("METRICS_APP_NAME", APP_NAME)
