from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

import views

urlpatterns = patterns('',
        (r'^$', views.app_index),
        (r'^(?P<app_name>[^/]+)/$', views.app_settings),
    )

# vim: et sw=4 sts=4
