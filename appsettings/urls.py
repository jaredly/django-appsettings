from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

import views

urlpatterns = patterns('',
        url(r'^$', views.app_index, name='index'),
        url(r'^(?P<app_name>[^/]+)/$', views.app_settings, name='app_settings'),
    )

# vim: et sw=4 sts=4
