from django import forms
from settingsobj import Settings
settings = Settings.single

_form = None

def settings_form():
    global _form
    if not _form:
        fields = {}
        for app_name in sorted(vars(settings).keys()):
            app = getattr(settings, app_name)
            for group_name, group in app._vals.iteritems():
                if group._readonly:continue
                for key, value in group._vals.iteritems():
                    fields['%s-%s-%s' % (app_name, group_name, key)] = value
        _form = type('SettingsForm', (forms.BaseForm,), {'base_fields':fields})
    return _form

# vim: et sw=4 sts=4
