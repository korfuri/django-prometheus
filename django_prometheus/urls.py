from django.urls import path

from django_prometheus import exports

urlpatterns = [path("metrics", exports.ExportToDjangoView, name="prometheus-django-metrics")]
