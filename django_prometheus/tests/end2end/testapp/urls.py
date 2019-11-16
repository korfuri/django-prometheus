from django.conf.urls import include, url
from django.contrib import admin
from testapp import views

urlpatterns = [
    url(r"^$", views.index),
    url(r"^help$", views.help),
    url(r"^slow$", views.slow, name="slow"),
    url(r"^objection$", views.objection),
    url(r"^sql$", views.sql),
    url(r"^newlawn/(?P<location>[a-zA-Z0-9 ]+)$", views.newlawn),
    url(r"^file$", views.file),
    url("", include("django_prometheus.urls")),
    url(r"^admin/", admin.site.urls),
]
