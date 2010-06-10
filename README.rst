Django appsettings
==================

finally, a unified system for pluggable apps to have configurable settings.
the django-appsettings app provides a clean api for keeping track of settings,
and, most importantly, having settings that are configurable for a user that
does not have write access to your server :) appsettings also provides an
interface (similar to the admin interface for models) for editing these
settings.

Features
--------

- an organized system for managing settings
- degrades gracefully when there's no database (settings will just be read-only)
- uses forms.Field classes to store setting types -- totally customizeable for
  - validation
  - serialization
  - display widgets
- supports full user overrides in project/settings.py
- **new:** special flags for *readonly* and *global* groups
- **new:** support for caching
- **new:** middleware to limit database access.

Todo
----

- improve the web interface
- add import/export via conf files

Usage
=====

So you want to use this in your app? Well, just create a settings.py for your
app (which will be auto-loaded by appsettings in the same way contrib.admin
loads your admin.py) and register your settings. Example::

    import appsettings
    from django import forms
    register = appsettings.register('mymodule')

    # settings are organized into groups.
    # this will define settings
    #   mymodule.story.greeting, 
    #   mymodule.story.pigs,
    #   etc.
    @register
    class Story:
        # int, string, and float types are auto-discovered.
        greeting = "hello"
        pigs = 3
        wolves = 1
        # or you can specify the type
        houses = forms.IntegerField(initial = 3, doc = "number of houses in which to hide")
        myhouse = forms.ChoiceField(choices = (('straw', 'Straw'),
                                             ('sticks', 'Sticks'),
                                             ('bricks', 'Bricks')),
                                    initial = 'straw')

Using the settings in the rest of your app couldn't be easier::

    from appsettings import app
    settings = app.settings.mymodule

    def run_away():
        return "%s pigs are running into a house made of %s" \
                        % (settings.story.pigs, settings.story.myhouse)

To enable users to edit the settings from the front end, add the following line to urls.py::

    url(r'^appsettings/', include('appsettings.urls')),

If a user change the settings (from the front end) then they will be saved to the database. The settings will then be retrieved from the database whenever they are used. Retrieving the settings from the database in this way could be time / resource expensive so there are two options to speed this up:

1. Enable caching.

 If caching is enabled the settings will be stored in the cache at initialisation time then retrieved and set to the cache whenever the settings are accessed or changed. As long as the cache backend supports cross-process caching then all threads will share the same settings.

 To enable caching, add the following line to your main settings.py::

    APPSETTINGS_USE_CACHE = True

 and set CACHE_BACKEND to something that supports cross-process caching (i.e.: NOT 'locmem://')

2. Use the SettingsMiddleware

 The SettingsMiddleware will copy all the settings stored in the database into the current request (thread) at the start of the request so that they do not need to be retrieved eache time they are accessed (during the request). 

 To use the middleware add ''appsettings.middleware.SettingsMiddleware' to the MIDDLEWARE_CLASSES in your project's setttings.py

 e.g::

    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'appsettings.middleware.SettingsMiddleware',
    )

.. note::

    As you can see, group names are converted to *lowercase* when accessing.
    This is to follow the django convention set in models and other areas, and
    because I think it looks better. If you have a good argument either way,
    feel free to make an `issue <http://github.com/jabapyth/django-appsettings/issues>`_.

Special Flags
-------------

appsettings also supports a few special flags, to make settings management
easier. Currently *readonly* and *main* are supported. *readonly* makes
a settings group, as you can imagine, read-only; they never interact with the
database. *main* makes the settings accessible outside of their group.
See example::

    ## -- walks/settings.py --
    import appsettings
    register = appsettings.register('walks')

    @register(main=True)
    class Globals:
        spam = 'spam and eggs'

    ## -- somewhere_else.py --

    import appsettings
    settings = appsettings.settings.walks

    print settings.spam ## gets routed to settings.globals.spam
    print settings.globals.spam

Note that you can only have one settings group flagged as "main".

Please give me feedback and any questions through github
http://github.com/jabapyth/django-appsettings
