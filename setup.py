import os
from distutils.core import setup


setup(
    name='django-appsettings',
    version='0.1b',
    description='A unified settings system for pluggable django apps',
    author='Jared Forsyth',
    author_email='jabapyth@gmail.com',
    license='BSD',
    url='http://github.com/jabapyth/django-appsettings/',
    keywords = ['django', 'settings', 'database', 'user', 'customize'],
    packages=[
        'appsettings',
    ],
    package_data = {'feedback': ['templates/appsettings/*']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
