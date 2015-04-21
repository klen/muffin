import os.path
import re

from aiohttp import web


DYNS_RE = re.compile(r'(\{[^{}]*\})')
DYNR_RE = re.compile(r'^\{(?P<var>[a-zA-Z][_a-zA-Z0-9]*)(?::(?P<re>.+))*\}$')


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

    def url(self, *, parts, query=None):
        """ Skip URL calculation. """
        raise NotImplemented

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
        filepath = os.path.join(self._directory, filename)
        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            return None

        return {'filename': path[self._prefix_len:]}
