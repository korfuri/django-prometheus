import django

if django.VERSION < (1, 4, 0):
    from django.conf.urls.defaults import url
else:
    from django.conf.urls import url

from django_prometheus import exports


urlpatterns = [
    url(r'^metrics$', exports.ExportToDjangoView,
        name='prometheus-django-metrics'),
]
