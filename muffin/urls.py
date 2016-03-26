"""URL helpers."""
import re
import asyncio
from random import choice
from string import printable
from urllib.parse import unquote

from aiohttp.hdrs import METH_ANY
from aiohttp.web import AbstractRoute, Resource, StaticRoute as VanilaStaticRoute, UrlDispatcher


DYNS_RE = re.compile(r'(\{[^{}]*\})')
DYNR_RE = re.compile(r'^\{(?P<var>[a-zA-Z][_a-zA-Z0-9]*)(?::(?P<re>.+))*\}$')
RETYPE = type(re.compile('@'))


class RawReResource(Resource):

    """Allow any regexp in routes."""

    def __init__(self, pattern, name=None):
        """Ensure that the pattern is regexp."""
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        self._pattern = pattern
        super(RawReResource, self).__init__(name=name)

    def get_info(self):
        """Get the resource's information."""
        return {'name': self._name, 'pattern': self._pattern}

    def _match(self, path):
        match = self._pattern.match(path)
        if match is None:
            return None
        return {key: unquote(value) for key, value in match.groupdict('').items()}

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
        return "<RawReResource '%s' %s>" % (self.name or '', self._pattern)


# TODO: Remove me when aiohttp > 0.21.2 will be relased. See #794
class StaticResource(Resource):

    def __init__(self, route):
        super(StaticResource, self).__init__()

        assert isinstance(route, AbstractRoute), \
            'Instance of Route class is required, got {!r}'.format(route)
        self._route = route
        self._routes.append(route)

    def url(self, **kwargs):
        return self._route.url(**kwargs)

    def get_info(self):
        return self._route.get_info()

    def _match(self, path):
        return self._route.match(path)

    def __len__(self):
        return 1

    def __iter__(self):
        yield self._route


class ParentResource(Resource):

    def __init__(self, path, *, name=None):
        super(ParentResource, self).__init__(name=name)
        self._path = path.rstrip('/')
        self.router = UrlDispatcher()

    @asyncio.coroutine
    def resolve(self, method, path):
        allowed_methods = set()
        if not path.startswith(self._path + '/'):
            return None, allowed_methods

        path = path[len(self._path):]

        for resource in self.router._resources:
            match_dict, allowed = yield from resource.resolve(method, path)
            if match_dict is not None:
                return match_dict, allowed_methods
            else:
                allowed_methods |= allowed
        return None, allowed_methods

    def add_resource(self, path, *, name=None):
        """Add resource."""
        return self.router.add_resource(path, name=name)

    def get_info(self):
        return {'path': self._path}

    def url(self, name=None, **kwargs):
        if name:
            return self._path + self.router[name].url(**kwargs)
        return self._path + '/'


class StaticRoute(VanilaStaticRoute):

    """Support multiple static resorces."""

    def match(self, path):
        """Check for file is exists."""
        if not path.startswith(self._prefix):
            return None

        filename = path[self._prefix_len:]
        try:
            self._directory.joinpath(filename).resolve()
            return {'filename': filename}
        except (ValueError, FileNotFoundError):
            return None


def routes_register(app, handler, *paths, methods=None, router=None, name=None):
    """Register routes."""
    if router is None:
        router = app.router

    resources = []

    for path in paths:

        # Register any exception to app
        if isinstance(path, type) and issubclass(path, Exception):
            app._error_handlers[path] = handler
            continue

        # Ensure that names are unique
        name = str(name or '')
        rname, rnum = name, 2
        while rname in router:
            rname = "%s%d" % (name, rnum)
            rnum += 1

        path = parse(path)
        if isinstance(path, RETYPE):
            resource = RawReResource(path, name=rname)
            router._reg_resource(resource)

        else:
            resource = router.add_resource(path, name=rname)

        for method in methods or [METH_ANY]:
            method = method.upper()

            # Muffin allows to use any method
            if method not in AbstractRoute.METHODS:
                AbstractRoute.METHODS.add(method)

            resource.add_route(method, handler)

        resources.append(resource)

    return resources


def parse(path):
    """Parse URL path and convert it to regexp if needed."""
    parsed = re.sre_parse.parse(path)
    for case, _ in parsed:
        if case not in (re.sre_parse.LITERAL, re.sre_parse.ANY):
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
            yield from getattr(self, "state_" + str(state).lower(), self.state_default)(value)

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
        if not value or not value[0]:
            for val in self.literals - set(value):
                return (yield val)
        yield value[0]

    state_branch = state_in

    @staticmethod
    def state_category(value):
        """Parse categories."""
        if value == re.sre_parse.CATEGORY_DIGIT:
            return (yield '0')

        if value == re.sre_parse.CATEGORY_WORD:
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
