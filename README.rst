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

using the settings in the rest of your app couldn't be easier::

    import appsettings
    settings = appsettings.settings.mymodule

    def run_away():
        return "%s pigs are running into a house made of %s" \
                        % (settings.story.pigs, settings.story.myhouse)

Special Flags
-------------

appsettings also supports a few special flags, to make settings management
easier. Currently *readonly* and *nogroup* are supported. *readonly* makes
a settings group, as you can imagine, readonly; they never interact with the
database. *nogroup* makes the settings accessible outside of their group.
See example::

    ## -- walks/settings.py --
    import appsettings
    register = appsettings.register('walks')

    @register(nogroup=True)
    class Globals:
        spam = 'spam and eggs'

    ## -- somewhere_else.py --

    import appsettings
    settings = appsettings.settings.walks

    print settings.spam ## gets routed to settings.globals.spam
    print settings.globals.spam

Please give me feedback and any questions through github
http://github.com/jabapyth/django-appsettings
