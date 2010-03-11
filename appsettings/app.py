import settingsobj
settings = settingsobj.Settings()
def register(appname):
    """register your settings with appsettings. usually used as a @decorator
    e.g.
    register = appsettings.register('appname')
    @register
    class Settingsgroup:
        ...
    """
    def meta(*args, **kwargs):
        if not args and kwargs:
            return lambda classobj:settingsobj.Settings.single._register(appname, classobj, **kwargs)
        if len(args)!=1:
            raise TypeError, "register(classobj) takes one argument, %d given" % (len(args))
        return settingsobj.Settings.single._register(appname, args[0], **kwargs)
    return meta

# vim: et sw=4 sts=4
