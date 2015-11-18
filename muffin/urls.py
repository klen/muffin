"""URL helpers."""
import re
import warnings
from os import path as ospath
from random import choice
from string import printable

from aiohttp import web
from aiohttp.hdrs import METH_ANY


DYNS_RE = re.compile(r'(\{[^{}]*\})')
DYNR_RE = re.compile(r'^\{(?P<var>[a-zA-Z][_a-zA-Z0-9]*)(?::(?P<re>.+))*\}$')
RETYPE = type(re.compile('@'))


def sre(path):
    """Support extended routes syntax.

    Depricated since 0.3.0.
    """
    warnings.warn('Muffin.sre is depricated. The functionality will be removed in 0.4.0')
    return path


class RawReRoute(web.DynamicRoute):

    """Support raw regular expresssions."""

    def __init__(self, method, handler, name, pattern, *, expect_handler=None):
        """Skip a formatter."""
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        super().__init__(method, handler, name, pattern, None, expect_handler=expect_handler)

    def match(self, path):
        """Match given path."""
        match = self._pattern.match(path)
        if match is None:
            return None
        return match.groupdict('')

    def url(self, *subgroups, query=None, **groups):
        """Build URL."""
        parsed = re.sre_parse.parse(self._pattern.pattern)
        subgroups = {n:str(v) for n, v in enumerate(subgroups, 1)}
        groups_ = dict(parsed.pattern.groupdict)
        subgroups.update({
            groups_[k0]: str(v0)
            for k0, v0 in groups.items()
            if k0 in groups_
        })
        url = ''.join(str(val) for val in Traverser(parsed, subgroups))
        return self._append_query(url, query)

    def __repr__(self):
        """Fix representation."""
        name = "'" + self.name + "' " if self.name is not None else ""
        return "<RawReRoute {name}[{method}] {pattern} -> {handler!r}".format(
            name=name, method=self.method, pattern=self._pattern, handler=self.handler)


class StaticRoute(web.StaticRoute):

    """Support multiple static resorces."""

    def match(self, path):
        """Check for file is exists."""
        if not path.startswith(self._prefix):
            return None

        filename = path[self._prefix_len:]
        filepath = ospath.join(self._directory, filename)
        if not ospath.isfile(filepath):
            return None

        return {'filename': path[self._prefix_len:]}


def routes_register(app, view, *paths, methods=None, router=None, name=''):
    """Register routes."""
    if router is None:
        router = app.router

    methods = methods or [METH_ANY]
    routes = []

    for method in methods:
        for path in paths:

            # Register any exception to app
            if isinstance(path, type) and issubclass(path, Exception):
                app._error_handlers[path] = view
                continue

            num = 1
            cname = name

            # Ensure that the route's name is unique
            if cname in router:
                method_ = method.lower().replace('*', 'any')
                cname, num = name + "." + method_, 1
                while cname in router:
                    cname = "%s%d.%s" % (name, num, method_)
                    num += 1

            # Is the path a regexp?
            path = parse(path)

            # Support regex as path
            if isinstance(path, RETYPE):
                routes.append(router.register_route(RawReRoute(method.upper(), view, cname, path)))
                continue

            # Support custom methods
            method = method.upper()
            if method not in router.METHODS:
                router.METHODS.add(method)

            routes.append(router.add_route(method, path, view, name=cname))

    return routes


def parse(path):
    """Parse URL path and convert it to regexp if needed."""
    parsed = re.sre_parse.parse(path)
    for case, _ in parsed:
        if case not in ('literal', 'any'):
            break
    else:
        return path

    path = path.strip('^$')

    def parse_(match):
        [part] = match.groups()
        match = DYNR_RE.match(part)
        params = match.groupdict()
        return '(?P<%s>%s)' % (params['var'], params['re'] or '[^{}/]+')

    return re.compile('^%s$' % DYNS_RE.sub(parse_, path))


class Traverser:

    """Traverse parsed regexp and build string."""

    literals = set(printable)

    def __init__(self, parsed, groups=None):
        """Initialize the traverser."""
        self.parsed = parsed
        self.groups = groups

    def __iter__(self):
        """Iterate builded parts."""
        for state, value in self.parsed:
            yield from getattr(self, "state_" + state, self.state_default)(value)

    def __next__(self):
        """Make self as generator."""
        yield from self

    @staticmethod
    def state_default(value):
        """Any unparsed state."""
        yield ''

    @staticmethod
    def state_literal(value):
        """Parse literal."""
        yield chr(value)

    def state_not_literal(self, value):
        """Parse not literal."""
        value = negate = chr(value)
        while value == negate:
            value = choice(self.literals)
        yield value

    def state_max_repeat(self, value):
        """Parse repeatable parts."""
        min_, max_, value = value
        value = [val for val in Traverser(value, self.groups)]
        if not min_ and max_:
            for val in value:
                if isinstance(val, required):
                    min_ = 1
                    break

        for val in value * min_:
            yield val

    state_min_repeat = state_max_repeat

    def state_in(self, value):
        """Parse ranges."""
        value = [val for val in Traverser(value, self.groups)]
        if not value[0]:
            for val in self.literals - set(value):
                return (yield val)
        yield value[0]

    state_branch = state_in

    @staticmethod
    def state_category(value):
        """Parse categories."""
        if value == 'category_digit':
            return (yield '0')

        if value == 'category_word':
            return (yield 'x')

    def state_subpattern(self, value):
        """Parse subpatterns."""
        num, parsed = value
        if num in self.groups:
            return (yield required(self.groups[num]))

        yield from Traverser(parsed, groups=self.groups)


class required:

    """Mark string part as required."""

    def __init__(self, string):
        """Initialize the object."""
        self.string = string

    def __str__(self):
        """Return self as string."""
        return self.string

    def __repr__(self):
        """String representation."""
        return "'%s'" % self

#  pylama:ignore=W0212
