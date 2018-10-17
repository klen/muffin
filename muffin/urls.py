"""URL helpers."""
import re
from pathlib import Path
from random import choice
from string import printable
from urllib.parse import unquote

from aiohttp.hdrs import METH_ANY
from aiohttp.web import (
    Resource,
    StaticResource,
)
from yarl import URL

from .utils import to_coroutine


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
        super().__init__(name=name)

    @property
    def canonical(self):
        return self._pattern.pattern

    def url_for(self, *subgroups, **groups):
        """Build URL."""
        parsed = re.sre_parse.parse(self._pattern.pattern)
        subgroups = {n:str(v) for n, v in enumerate(subgroups, 1)}
        groups_ = dict(parsed.pattern.groupdict)
        subgroups.update({
            groups_[k0]: str(v0)
            for k0, v0 in groups.items()
            if k0 in groups_
        })
        path = ''.join(str(val) for val in Traverser(parsed, subgroups))
        return URL.build(path=path, encoded=True)

    def _match(self, path):
        match = self.raw_match(path)
        if match is None:
            return None
        return {key: unquote(value) for key, value in match.groupdict('').items()}

    def add_prefix(self, prefix):
        self._pattern = re.compile(re.escape(prefix) + self._pattern.pattern.strip('^'))

    def get_info(self):
        """Get the resource's information."""
        return {'name': self._name, 'pattern': self._pattern}

    def raw_match(self, path):
        return self._pattern.match(path)

    def __repr__(self):
        """Fix representation."""
        return "<RawReResource '%s' %s>" % (self.name or '', self._pattern)


class SafeStaticResource(StaticResource):
    """Doesn't match for non-existing files.."""

    async def resolve(self, request):
        match_info, methods = await super().resolve(request)
        if match_info:
            rel_url = match_info['filename']
            try:
                filename = Path(rel_url)
                if filename.anchor:
                    return None, set()

                filepath = self._directory.joinpath(filename).resolve()
                if filepath.exists():
                    return match_info, methods

            except (ValueError, FileNotFoundError) as error:
                # relatively safe
                return None, set()

        return None, set()


def routes_register(app, handler, *paths, methods=None, router=None, name=None):
    """Register routes."""
    if router is None:
        router = app.router

    handler = to_coroutine(handler)

    resources = []

    for path in paths:

        # Register any exception to app
        if isinstance(path, type) and issubclass(path, BaseException):
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
            router.register_resource(resource)

        else:
            resource = router.add_resource(path, name=rname)

        for method in methods or [METH_ANY]:
            method = method.upper()
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
        num, *_, parsed = value
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
