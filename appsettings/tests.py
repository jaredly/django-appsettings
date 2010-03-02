"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
import settingsobj, values

class Cheese:
    color = 'white'
    age = 5
    type = values.ChoiceValue(['american','ricotta','fetta'], 'ricotta')

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
        self.assert_(hasattr(self.settings.test, 'cheese'))
        self.assert_(hasattr(self.settings.test.cheese, 'color'))
        self.assert_(hasattr(self.settings.test.cheese, 'age'))
        self.assert_(hasattr(self.settings.test.cheese, 'type'))

    def testAutoMagic(self):
        self.assertEquals(self.settings.test.cheese._vals['color'].__class__, values.StringValue)
        self.assert_(isinstance(self.settings.test.cheese._vals['color'], values.StringValue))
        self.assert_(isinstance(self.settings.test.cheese._vals['age'], values.IntValue))
        self.assert_(isinstance(self.settings.test.cheese._vals['type'], values.ChoiceValue))

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

