try:
    from django import db
    from django.db.backends.dummy import base
    from models import Setting
    has_db = not isinstance(db.connection, base.DatabaseWrapper)
    numsettings = Setting.objects.all().count()
except:
    has_db = False

import inspect
from models import Setting
from django.contrib.sites.models import Site
from django.utils.encoding import force_unicode
from django import forms
from django.core.cache import cache


from appsettings import user
import appsettings

class SettingsException(Exception):pass
class MultipleSettingsException(Exception):pass


class Settings(object):
    discovered = False
    using_middleware = False
    _state = { }
    # see http://code.activestate.com/recipes/66531/
    def __new__(cls, *p, **k):
        self = object.__new__(cls, *p, **k)
        self.__dict__ = cls._state
        return self

    @classmethod
    def _reset(cls):
        """Reset all `Settings` object to the initial empty condition."""
        cls._state = { }

    def _register(self, appname, classobj, readonly=False, main=False):
        if not hasattr(self, appname):
            setattr(self, appname, App(appname))
        getattr(self, appname)._add(classobj, readonly, main, getattr(user.settings, appname)._dct)

    def update_from_db(self):
        if has_db:
            settings = Setting.objects.all()
            for setting in settings:
                app = getattr(self, setting.app)
                if app._vals.has_key(setting.class_name):
                    group = app._vals[setting.class_name]
                    if group._vals.has_key(setting.key):
                        group._vals[setting.key].initial = group._vals[setting.key].clean(setting.value)
                    else:
                        ## the app removed the setting... shouldn't happen
                        ## in production. maybe error? or del it?
                        pass


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
                if name in self._vals[self._main]._vals:
                    return getattr(self._vals[self._main], name)
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
        self._verbose_name = name
        self._vals = {}
        self._readonly = False
        self._cache_prefix = 'appsetting-%s-%s-%s-' % (Site.objects.get_current().pk, self._appname, self._name)

        for attr in inspect.classify_class_attrs(classobj):
            # for Python 2.5 compatiblity, we use tuple indexes
            # instead of the attribute names (which are only available
            # from Python 2.6 onwards).  Here's the mapping:
            #   attr[0]  attr.name   Attribute name
            #   attr[1]  attr.kind   class/static method, property, data
            #   attr[2]  attr.defining_class  The `class` object that created this attr
            #   attr[3]  attr.object Attribute value
            #
            if attr[2] != classobj or attr[1] != 'data':
                continue
            if attr[0].startswith('_'):
                continue
            if attr[0] == 'verbose_name':
                self._verbose_name = attr[3]
                continue
            val = attr[3]
            key = attr[0]
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
        if name not in ('_vals', '_name', '_appname', '_verbose_name', '_readonly', '_cache_prefix'):
            if name not in self._vals:
                raise AttributeError, 'setting "%s" not found'%name
            if has_db:
                if appsettings.USE_CACHE and cache.has_key(self._cache_prefix+name):
                    return cache.get(self._cache_prefix+name)
                if not Settings.using_middleware:
                    try:
                        setting = Setting.objects.get(app=self._appname, class_name=self._name, key=name)
                    except Setting.DoesNotExist:
                        pass
                    else:
                        return self._vals[setting.key].clean(setting.value)
            return self._vals[name].initial
        return super(Group, self).__getattribute__(name)

    def __setattr__(self, name, value):
        if name in ('_vals', '_name', '_appname', '_verbose_name', '_readonly', '_cache_prefix'):
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
        if appsettings.USE_CACHE:
            cache.set(self._cache_prefix+name, value)

# vim: et sw=4 sts=4
