from django.conf import settings
from django.http import HttpResponseRedirect
from appsettings.settingsobj import has_db
from settingsobj import Settings
settingsinst = Settings()

Settings.using_middleware = True



class SettingsMiddleware(object):
    """
    Load the settings from the database for each request (thread), do not use with caching.
    """
    def process_request(self, request):
        settingsinst.update_from_db()

