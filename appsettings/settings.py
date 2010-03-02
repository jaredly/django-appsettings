import appsettings
register = appsettings.register('appsettings')

@register
class Base:
    greeting = 'Hello, neo'

# vim: et sw=4 sts=4
