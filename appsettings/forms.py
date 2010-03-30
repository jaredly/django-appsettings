from django import forms
from settingsobj import Settings
settings = Settings.single

_form = None

class Fieldset(object):
    def __init__(self, form, fields):
        self.form = form
        self.fields = fields
        
    def __iter__(self):
        for name in self.fields:
            yield self.form[name]

    def __getitem__(self, name):
        "Returns a BoundField with the given name."
        try:
            return self.form[name]
        except KeyError:
            raise KeyError('Key %r not found in Form' % name)

class FieldsetForm(forms.BaseForm):
    def __init__(self, *args, **kwargs):
        super(FieldsetForm, self).__init__(*args, **kwargs)
        self.fieldsets = {}
        for fieldset_name, fields in self.base_fieldsets.items():
            self.fieldsets[fieldset_name] = Fieldset(self, fields)


def settings_form():
    global _form
    if not _form:
        fields = {}
        fieldsets = {}
        for app_name in sorted(vars(settings).keys()):
            app = getattr(settings, app_name)
            for group_name, group in app._vals.iteritems():
                if group._readonly:continue
                fieldset_fields = []
                for key, value in group._vals.iteritems():
                    field_name = '%s-%s-%s' % (app_name, group_name, key)
                    fields[field_name] = value
                    fieldset_fields.append(field_name)
                fieldsets[group_name] = fieldset_fields
        _form = type('SettingsForm', (FieldsetForm,),
                     {'base_fieldsets': fieldsets, 'base_fields':fields})
#        _form.fieldsets = fieldsets
    return _form

# vim: et sw=4 sts=4
