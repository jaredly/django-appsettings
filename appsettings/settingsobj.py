try:
    from django import db
    from django.db.backends.dummy import base
    has_db = not isinstance(db.connection, base.DatabaseWrapper)
except:
    has_db = False

import inspect
from models import Setting
from django.contrib.sites.models import Site
from values import *

class SettingsException(Exception):pass

class Settings(object):
    single = None
    def __init__(self):
        if Settings.single is not None:
            raise MultipleSettingsException, \
                "can only have one settings instance"
        Settings.single = self
    
    def _register(self, appname, classobj):
        if not hasattr(self, appname):
            setattr(self, appname, App(appname))
        getattr(self, appname)._add(classobj)

class App(object):
    def __init__(self, app):
        self._name = app
        self._vals = {}

    def _add(self, classobj):
        name = classobj.__name__.lower()
        if name in self._vals:
            raise SettingsException, 'duplicate declaration of %s'%name
        if name in ('_vals','_add','_name'):
            raise SettingsException, 'invalid setting name'
        self._vals[name] = Group(self._name, name, classobj)

    def __getattr__(self, name):
        if name not in ('_vals', '_name', '_add'):
            if name not in self._vals:
                if 'basic' in self._vals and name in self.basic._vals:
                    return getattr(self.basic, name)
                raise SettingsException, 'group not found'
            return self._vals[name]
        return super(App, self).__getattribute__(name)

    def __setattr__(self, name, val):
        if name not in ('_vals', '_name', '_add'):
            raise SettingsException, 'groups are immutable'
        super(App, self).__setattr__(name, val)

class Group(object):
    def __init__(self, appname, name, classobj):
        self._appname = appname
        self._name = name
        self._vals = {}

        for attr in inspect.classify_class_attrs(classobj):
            if attr.defining_class != classobj or attr.kind != 'data' or attr.name.startswith('_'):
                continue
            val = attr.object
            key = attr.name
            if type(val) == int:
                val = IntValue(val)
            elif type(val) == float:
                val = FloatValue(val)
            elif type(val) == str:
                val = StringValue(val)
            elif val in (True, False):
                val = BoolValue(val)
            elif not isinstance(val, Value):
                raise SettingsException, "unknown setting type for value '%s' and key '%s'" % (val, key)
            val._parent = self
            self._vals[key] = val
        if has_db:
            settings = Setting.objects.all().filter(app=self._appname,
                    class_name=self._name)
            for setting in settings:
                if self._vals.has_key(setting.key):
                    self._vals[setting.key].loadval(setting.value)
                else:
                    ## the app removed the setting... shouldn't happen 
                    ## in production. maybe error? or del it?
                    pass

    def __getattr__(self, name):
        if name not in ('_vals', '_name', '_appname'):
            if name not in self._vals:
                raise AttributeError, 'setting "%s" not found'%name
            return self._vals[name].val
        return super(Group, self).__getattribute__(name)

    def __setattr__(self, name, value):
        if name in ('_vals', '_name', '_add', '_appname'):
            return object.__setattr__(self, name, value)
            #setattr(super(Group, self), name, value)
            #return object.__setattribute__(self, name, value)
        if not name in self._vals:
            raise AttributeError, 'setting "%s" not found'%name
        if not has_db:
            raise SettingsException, "no database -- settings are immutable"
        if not self._vals[name].validate(value):
            raise ValueError, 'invalid value "%s" for setting type %s'%(value, 
                    self._vals[name].__class__.__name__)
        try:
            setting = Setting.objects.get(app = self._appname,
                    class_name = self._name,
                    key = name)
        except Setting.DoesNotExist:
            setting = Setting(site = Site.objects.get_current(), app = self._appname, class_name = self._name, key = name)
        setting.value = self._vals[name].serialize(value)
        setting.save()
        self._vals[name].val = value

# vim: et sw=4 sts=4
