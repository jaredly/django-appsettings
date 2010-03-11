try:
    from django import db
    from django.db.backends.dummy import base
    has_db = not isinstance(db.connection, base.DatabaseWrapper)
except:
    has_db = False

import inspect
from models import Setting
from django.contrib.sites.models import Site
from django.utils.encoding import force_unicode
from django import forms

from appsettings import user

class SettingsException(Exception):pass
class MultipleSettingsException(Exception):pass

class Settings(object):
    single = None
    def __init__(self):
        if Settings.single is not None:
            raise MultipleSettingsException, \
                "can only have one settings instance"
        Settings.single = self
    
    def _register(self, appname, classobj, readonly=False, main=False):
        if not hasattr(self, appname):
            setattr(self, appname, App(appname))
        getattr(self, appname)._add(classobj, readonly, main, getattr(user.settings, appname)._dct)

class App(object):
    def __init__(self, app):
        self._name = app
        self._vals = {}
        self._main = None

    def _add(self, classobj, readonly, main, preset):
        name = classobj.__name__.lower()
        if name in self._vals or (self._main is not None and name in self._vals[self._main]):
            raise SettingsException, 'duplicate declaration of settings group %s.%s' % (self._name, name)
        if name in ('_vals','_add','_name'):
            raise SettingsException, 'invalid group name: %s' % name

        if not main:
            preset = preset.get(name, {})
        self._vals[name] = Group(self._name, name, classobj, preset, main)
        if readonly:
            self._vals[name]._readonly = readonly
        if main:
            if self._main is not None:
                raise SettingsException, 'multiple "main" groups defined for app %s' % self._name
            self._main = name

    def __getattr__(self, name):
        if name not in ('_vals', '_name', '_add', '_main'):
            if name not in self._vals and self._main:
                if name in self._vals[self._name]._vals:
                    return getattr(self._vals[self._name], name)
                raise SettingsException, 'group not found: %s' % name
            return self._vals[name]
        return super(App, self).__getattribute__(name)

    def __setattr__(self, name, val):
        if name not in ('_vals', '_name', '_add', '_main') and self._main:
            if name in self._vals[self._name]._vals:
                return setattr(self._vals[self._name], name, val)
            raise SettingsException, 'groups are immutable'
        super(App, self).__setattr__(name, val)

class Group(object):
    def __init__(self, appname, name, classobj, preset, main=False):
        self._appname = appname
        self._name = name
        self._vals = {}
        self._readonly = False

        for attr in inspect.classify_class_attrs(classobj):
            if attr.defining_class != classobj or attr.kind != 'data':
                continue
            if attr.name.startswith('_'):
                continue
            val = attr.object
            key = attr.name
            if type(val) == int:
                val = forms.IntegerField(label=key.title(), initial=val)
            elif type(val) == float:
                val = forms.FloatField(label=key.title(), initial=val)
            elif type(val) == str:
                val = forms.CharField(label=key.title(), initial=val)
            elif val in (True, False):
                val = forms.BooleanField(label=key.title(), initial=val)
            elif not isinstance(val, forms.Field):
                raise SettingsException, 'settings must be of a valid form field type'
            if preset.has_key(key):
                val.initial = preset[key]
            try:
                val.initial = val.clean(val.initial)
            except forms.ValidationError:
                if main:
                    raise SettingsException, 'setting %s.%s not set. Please set it in your settings.py' % (appname, key)
                raise SettingsException, 'setting %s.%s.%s not set. Please set it in your settings.py' % (appname, name, key)
            val._parent = self
            self._vals[key] = val

        if has_db:
            settings = Setting.objects.all().filter(app=self._appname,
                    class_name=self._name)
            for setting in settings:
                if self._vals.has_key(setting.key):
                    self._vals[setting.key].initial = self._vals[setting.key].clean(setting.value)
                else:
                    ## the app removed the setting... shouldn't happen 
                    ## in production. maybe error? or del it?
                    pass

    def __getattr__(self, name):
        if name not in ('_vals', '_name', '_appname', '_readonly'):
            if name not in self._vals:
                raise AttributeError, 'setting "%s" not found'%name
            return self._vals[name].initial
        return super(Group, self).__getattribute__(name)

    def __setattr__(self, name, value):
        if name in ('_vals', '_name', '_appname', '_readonly'):
            return object.__setattr__(self, name, value)
        if self._readonly:
            raise AttributeError, 'settings group %s is read-only' % self._name
        if not name in self._vals:
            raise AttributeError, 'setting "%s" not found'%name
        if not has_db:
            raise SettingsException, "no database -- settings are immutable"
        self._vals[name].initial = self._vals[name].clean(value)
        try:
            setting = Setting.objects.get(app = self._appname,
                    site = Site.objects.get_current(), 
                    class_name = self._name,
                    key = name)
        except Setting.DoesNotExist:
            setting = Setting(site = Site.objects.get_current(), 
                    app = self._appname, 
                    class_name = self._name, 
                    key = name)
        serialized = value
        if hasattr(self._vals[name].widget, '_format_value'):
            serialized = self._vals[name].widget._format_value(value)
        serialized = force_unicode(serialized)
        setting.value = serialized
        setting.save()

# vim: et sw=4 sts=4
