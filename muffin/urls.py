#  import os.path
import re
from os import path as ospath

from aiohttp import web
from aiohttp.hdrs import METH_ANY


DYNS_RE = re.compile(r'(\{[^{}]*\})')
DYNR_RE = re.compile(r'^\{(?P<var>[a-zA-Z][_a-zA-Z0-9]*)(?::(?P<re>.+))*\}$')
RETYPE = type(re.compile('@'))


def sre(reg):
    """ Support `Muffin` URL RE. """
    reg = reg.strip('^$')

    def parse(match):
        [part] = match.groups()
        match = DYNR_RE.match(part)
        params = match.groupdict()
        return '(?P<%s>%s)' % (params['var'], params['re'] or '[^{}/]+')

    return re.compile('^%s$' % DYNS_RE.sub(parse, reg))


class RawReRoute(web.DynamicRoute):

    """ Support raw re. """

    def __init__(self, method, handler, name, pattern):
        """ Skip a formatter. """
        super().__init__(method, handler, name, pattern, None)

    def match(self, path):
        match = self._pattern.match(path)
        if match is None:
            return None
        return match.groupdict('')

    def url(self, *, parts, query=None):
        """ Not supported. """
        raise RuntimeError(".url() is not allowed for RawReRoute")

    def __repr__(self):
        """ Fix representation. """
        name = "'" + self.name + "' " if self.name is not None else ""
        return "<RawReRoute {name}[{method}] {pattern} -> {handler!r}".format(
            name=name, method=self.method, pattern=self._pattern, handler=self.handler)


class StaticRoute(web.StaticRoute):

    """ Support multiple static resorces. """

    def match(self, path):
        """ Check for file is exists. """
        if not path.startswith(self._prefix):
            return None

        filename = path[self._prefix_len:]
        filepath = ospath.join(self._directory, filename)
        if not ospath.exists(filepath) or not ospath.isfile(filepath):
            return None

        return {'filename': path[self._prefix_len:]}


def routes_register(app, view, *paths, methods=None, router=None, name=''):
    """ Register routes. """

    if router is None:
        router = app.router

    methods = methods or [METH_ANY]

    for method in methods:
        for path in paths:

            # Register any exception to app
            if isinstance(path, type) and issubclass(path, Exception):
                app._error_handlers[path] = view
                continue

            # Fix route name
            cname, num = name + "-" + method.lower(), 1
            while cname in router:
                cname = name + "-" + str(num)
                num += 1

            # Support regexpa in paths
            if isinstance(path, RETYPE):
                router.register_route(RawReRoute(method.upper(), view, cname, path))
                continue

            # Support custom methods
            method = method.upper()
            if method not in router.METHODS:
                router.METHODS.add(method)

            router.add_route(method, path, view, name=cname)
