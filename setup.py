import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-appsettings',
    version='0.1',
    description='A unified settings system for pluggable django apps',
    long_description=read('README.rst'),
    author='Jared Forsyth',
    author_email='jabapyth@gmail.com',
    license='BSD',
    url='http://github.com/jabapyth/django-appsettings/',
    keywords = ['django', 'settings', 'database', 'user', 'customize'],
    packages=[
        'appsettings',
    ],
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
