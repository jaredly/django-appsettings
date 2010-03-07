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

class SettingsException(Exception):pass
class MultipleSettingsException(Exception):pass

class Settings(object):
    single = None
    def __init__(self):
        if Settings.single is not None:
            raise MultipleSettingsException, \
                "can only have one settings instance"
        Settings.single = self
    
    def _register(self, appname, classobj, readonly=False, nogroup=False):
        if not hasattr(self, appname):
            setattr(self, appname, App(appname))
        getattr(self, appname)._add(classobj, readonly, nogroup)

class App(object):
    def __init__(self, app):
        self._name = app
        self._vals = {}
        self._nogroup = []

    def _add(self, classobj, readonly, nogroup):
        name = classobj.__name__.lower()
        if name in self._vals:
            raise SettingsException, 'duplicate declaration of %s'%name
        if name in ('_vals','_add','_name'):
            raise SettingsException, 'invalid group name: %s' % name
        self._vals[name] = Group(self._name, name, classobj)
        if readonly:
            self._vals[name]._readonly = readonly
        if nogroup:
            self._nogroup.append(name)

    def __getattr__(self, name):
        if name not in ('_vals', '_name', '_add', '_nogroup'):
            if name not in self._vals:
                for gname in self._nogroup:
                    if name in self._vals[gname]._vals:
                        return getattr(self._vals[gname], name)
                raise SettingsException, 'group not found: %s' % name
            return self._vals[name]
        return super(App, self).__getattribute__(name)

    def __setattr__(self, name, val):
        if name not in ('_vals', '_name', '_add', '_nogroup'):
            for gname in self._nogroup:
                if name in self._vals[gname]._vals:
                    return setattr(self._vals[gname], name, val)
            raise SettingsException, 'groups are immutable'
        super(App, self).__setattr__(name, val)

class Group(object):
    def __init__(self, appname, name, classobj):
        self._appname = appname
        self._name = name
        self._vals = {}
        self._readonly = False

        for attr in inspect.classify_class_attrs(classobj):
            if attr.defining_class != classobj or attr.kind != 'data':
                continue
            if attr.name.startswith('_'):
                ## TODO: decide whether to have _readonly etc. special names.
                #if attr.name == '_readonly':
                #    self._readonly = True
                #else:
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
