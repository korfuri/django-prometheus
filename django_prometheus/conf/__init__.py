import os

from django.conf import settings

APP_NAME = getattr(settings, 'METRICS_APP_NAME', 'django')
APP_NAME = os.getenv('METRICS_APP_NAME', APP_NAME)
