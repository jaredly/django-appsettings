from django.db import models
from django.contrib.sites.models import Site

class Setting(models.Model):
    site = models.ForeignKey(Site)
    app = models.CharField(max_length=255)
    class_name = models.CharField(max_length=255, blank=True)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255, blank=True)

    def __setattr__(self, name, value):
        if name != 'value':
            try:
                current = getattr(self, name, None)
            except:
                current = None
            if current is not None and current is not '':
                return
        super(Setting, self).__setattr__(name, value)

