import settingsobj

settings = settingsobj.Settings()
if not settingsobj.Settings.discovered:
    from appsettings import autodiscover
    autodiscover()

# vim: et sw=4 sts=4
