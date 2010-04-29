"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django import forms
import settingsobj
import appsettings

CHEESES = ('american','ricotta','fetta')
CHEESES = tuple((a,a) for a in CHEESES)

class Cheese:
    color = 'white'
    age = 5
    type = forms.ChoiceField(choices = CHEESES, initial='ricotta')

class RDOnly:
    version = 4

class Globals:
    spam = 'spamspamspam'

class SimpleTest(TestCase):
    def setUp(self):
        settingsobj.Settings._reset()
        self.settings = settingsobj.Settings()
        register = appsettings.register('test')
        register(Cheese)
        register(readonly=True)(RDOnly)
        register(Globals, main=True)

    def tearDown(self):
        settingsobj.Settings._reset()
        self.settings = None

    def testGroup(self):
        self.assert_(hasattr(self.settings, 'test'))

    def testHasSettings(self):
        settings = self.settings.test
        self.assert_(hasattr(settings, 'cheese'))
        self.assert_(hasattr(settings.cheese, 'color'))
        self.assert_(hasattr(settings.cheese, 'age'))
        self.assert_(hasattr(settings.cheese, 'type'))

    def testAutoMagic(self):
        settings = self.settings.test
        self.assert_(isinstance(settings.cheese._vals['color'], forms.CharField))
        self.assert_(isinstance(settings.cheese._vals['age'], forms.IntegerField))
        self.assert_(isinstance(settings.cheese._vals['type'], forms.ChoiceField))

    def testSetGet(self):
        settings = self.settings.test
        settings.cheese.color = 'blue'
        self.assertEquals(settings.cheese.color, 'blue')
        self.assertRaises(forms.ValidationError, settings.cheese.__setattr__, 'age', 'red')
        self.assertRaises(forms.ValidationError, settings.cheese.__setattr__, 'type', 4)
        self.assertRaises(forms.ValidationError, settings.cheese.__setattr__, 'type', 'blue')
        settings.cheese.type = 'american'
        self.assertEquals(settings.cheese.type, 'american')

    def testReadOnly(self):
        settings = self.settings.test
        self.assertRaises(AttributeError, settings.rdonly.__setattr__, 'version', 17)
        self.assertEquals(settings.rdonly.version, 4)

    def testNoGroup(self):
        settings = self.settings.test
        self.assertEquals(settings.spam, 'spamspamspam')
        self.assertEquals(settings.globals.spam, 'spamspamspam')


__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

