import django
from django_prometheus import exports

if django.VERSION < (1, 4, 0):
    from django.conf.urls.defaults import url
else:
    from django.conf.urls import url


urlpatterns = [
    url(r'^metrics$', exports.ExportToDjangoView,
        name='prometheus-django-metrics'),
]
