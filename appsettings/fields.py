from django.forms import widgets
from django import forms
from django.utils import simplejson
#from django.core import validators

class ListWidget(widgets.Input):
    input_type = 'text'

    def render(self, name, value, attrs=None):
        value = ', '.join(value)
        return super(ListWidget, self).render(name, value, attrs)

class ListField(forms.Field):
    widget = ListWidget
    default_error_messages = {}

    def to_python(self, value):
        """Validates the value and converts to python"""
        if value is None:
            return ()
        elif type(value) in (tuple, list):
            return tuple(value)
        elif type(value) in (str, unicode):
            return tuple(a.strip() for a in value.split(','))
        raise forms.ValidationError, 'invalid?'

class DictWidget(widgets.Input):
    input_type = 'text'
    def render(self, name, value, attrs=None):
        value = simplejson.dumps(value)
        return super(DictWidget, self).render(name, value, attrs)

class DictField(forms.Field):
    widget = DictWidget
    default_error_messages = {}

    def to_python(self, value):
        """Validates the value and converts to python"""
        if value is None:
            return {}
        elif type(value) is dict:
            return value
        elif type(value) in (str, unicode):
            value = json.loads(value)
            if type(value) is dict:
                return value
        raise forms.ValidationError, 'invalid input. requires a dictionary'




# vim: et sw=4 sts=4
