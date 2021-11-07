from django.contrib import admin
from django.urls import include, path, re_path
from testapp import views

urlpatterns = [
    re_path(r"^$", views.index),
    re_path(r"^help$", views.help),
    re_path(r"^slow$", views.slow, name="slow"),
    re_path(r"^objection$", views.objection),
    re_path(r"^sql$", views.sql),
    re_path(r"^newlawn/(?P<location>[a-zA-Z0-9 ]+)$", views.newlawn),
    re_path(r"^file$", views.file),
    path("", include("django_prometheus.urls")),
    re_path(r"^admin/", admin.site.urls),
]
