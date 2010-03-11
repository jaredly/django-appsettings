
class ProxyDict(object):
    def __init__(self, name, dct):
        self._name = name
        self._dct = dct[name] = {}
        self._proxies = {}
    def __getattr__(self, name):
        if name in ('_name', '_dct', '_proxies'):
            return super(ProxyDict, self).__getattr__(name)
        if not self._proxies.has_key(name):
            if name in self._dct:
                return self._dct[name]
            self._proxies[name] = ProxyDict(name, self._dct)
        return self._proxies[name]
    def __setattr__(self, name, val):
        if name in ('_name', '_dct', '_proxies'):
            return super(ProxyDict, self).__setattr__(name, val)
        self._dct[name] = val

settings = ProxyDict('main', {})

# vim: et sw=4 sts=4
