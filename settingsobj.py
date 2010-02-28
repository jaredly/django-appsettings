from django.db.backends.dummy import base
from django import db

has_db = not isinstance(db.connection, base.DatabaseWrapper)

class Settings:
    single = None
    def __init__(self):
        if Settings.single is not None:
            raise MultipleSettingsException,"can only have one settings instance"
        Settings.single = self
    
    def _register(self, appname, classobj):
        if not hasattr(self, appname):
            setattr(self, appname, App(appname))
        getattr(self, appname)._add(classobj)

class App:
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
                raise SettingsException, 'group not found'
            return self._vals[name]
        super(App, self).__getattr__(name)

    def __setattr__(self, name, val):
        if name not in ('_vals', '_name', '_add'):
            raise SettingsException, 'groups are immutable'
        super(App, self).__setattr__(name, val)

class Group:
    def __init__(self, appname, name, classobj):
        self._appname = appname
        self._name = name
        self._vals = {}

        for attr in inspect.classify_class_attrs(classobj):
            if not attr.defining_class != classobj or attr.kind != 'data':
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
                raise SettingsException, "unknown setting type for value '%s'" % val
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
        super(Group, self).__getattr__(name)

    def __setattr__(self, name, value):
        if name in ('_vals', '_name', '_add'):
            return super(Group, self).__setattr__(name, val)
        if not name in self._vals:
            raise AttributeError, 'setting "%s" not found'%name
        if not has_db:
            raise SettingsException, "no database -- settings are immutable"
        if not self._vals[name].validate(val):
            raise ValueError, 'invalid value "%s" for setting type %s'%(val, 
                    self._vals[name].__class__.__name__)
        setting = Setting.objects.get(app = self._appname,
                class_name = self._name,
                key = name)
        setting.value = str(value)
        setting.save()

class Value(object):
    def __init__(self, default, doc = ''):
        if not self.validate(default):
            raise ValueError, "invalid default value for type '%s'"%self.__class__.__name__
        self.val = default
        self.doc = doc
        self._parent = None

    def loadval(self, string):
        '''take a string, parse to actual value'''
        pass

    def validate(self, val):
        '''validate a value'''
        pass

class IntValue(Value):
    def loadval(self, string):
        self.val = int(string)
    def validate(self, val):
        return type(val) == int

class FloatValue(Value):
    def loadval(self, string):
        self.val = float(string)
    def validate(self, val):
        return type(val) in (float, int)

class StringValue(Value):
    def loadval(self, string):
        self.val = string
    def validate(self, val):
        return type(val) is str

class PercentValue(FloatValue):
    def validate(self, val):
        return type(val) in (int, float) and 0 <= val <= 1

class ChoiceValue(Value):
    def __init__(self, options, default, doc = ''):
        self.options = options
        Value.__init__(self, default, doc)
    def loadval(self, string):
        self.val = string
    def validate(self, val):
        return val in self.options

class BoolValue(Value):
    def loadval(self, string):
        self.val = string == 'True'
    def validate(self, val):
        return val in (True, False)

# vim: et sw=4 sts=4
