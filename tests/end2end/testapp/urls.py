from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^$', 'testapp.views.index'),
    url(r'^help$', 'testapp.views.help'),
    url(r'^slow$', 'testapp.views.slow'),
    url(r'^objection$', 'testapp.views.objection'),
    url(r'^admin/', include(admin.site.urls)),
]
