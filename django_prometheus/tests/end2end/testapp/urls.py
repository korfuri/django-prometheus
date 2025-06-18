from django.contrib import admin
from django.urls import include, path

from testapp import views

urlpatterns = [
    path("", views.index),
    path("help", views.help),
    path("slow", views.slow, name="slow"),
    path("objection", views.objection),
    path("sql", views.sql),
    path("newlawn/<str:location>", views.newlawn),
    path("file", views.file),
    path("", include("django_prometheus.urls")),
    path("admin/", admin.site.urls),
]
