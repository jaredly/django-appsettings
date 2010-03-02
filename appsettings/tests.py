"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django import forms
import settingsobj

CHEESES = ('american','ricotta','fetta')
CHEESES = tuple((a,a) for a in CHEESES)
class Cheese:
    color = 'white'
    age = 5
    type = forms.ChoiceField(choices = CHEESES, initial='ricotta')

class SimpleTest(TestCase):
    def setUp(self):
        settingsobj.Settings.single = None
        self.settings = settingsobj.Settings()
        self.settings._register('test',Cheese)

    def tearDown(self):
        settingsobj.Settings.single = None
        self.settings = None

    def testGroup(self):
        self.assert_(hasattr(self.settings, 'test'))

    def testSettings(self):
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

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

