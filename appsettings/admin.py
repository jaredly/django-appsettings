import appsettings
from django.contrib import admin
from appsettings.models import Setting

if appsettings.SHOW_ADMIN:
    admin.site.register(Setting)

# vim: et sw=4 sts=4
