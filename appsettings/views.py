# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from settingsobj import Settings
settingsinst = Settings.single
from models import Setting
import forms

@staff_member_required
def app_index(request, template = 'appsettings/index.html', base_template = 'index.html'):
    apps = sorted(vars(settingsinst).keys())
    return render_to_response(template, 
            {'apps':apps, 'base_template':base_template},
            RequestContext(request))

@staff_member_required
def app_settings(request, app_name=None, template = 'appsettings/settings.html', base_template = 'index.html'):
    editor = forms.settings_form()
    if request.POST:
        form = editor(request.POST)
        if form.is_valid():
            for key, value in form.fields.iteritems():
                app, group, name = key.split('-')
                val = form.cleaned_data[key]
                if val != getattr(settingsinst, app)._vals[group]._vals[name].initial:
                    setattr(getattr(settingsinst, app)._vals[group], name, val)
    else:
        form = editor()
    #fieldsets = construct_fieldsets(form, form.fieldsets)
    print form.fieldsets
    #assert False
    return render_to_response(template, 
                              {'app':app_name,'form':form, 'base_template':base_template},
                              context_instance=RequestContext(request))

def construct_fieldsets(form, fieldset_names):
    print form.fieldsets
    fieldsets = {}
    for group_name, fields in fieldset_names.items():
        fields = {}
        for field in fields:
            fields[field] = form.fields[field]
        fieldsets[group_name] = fields
    print fieldsets
    return fieldsets
