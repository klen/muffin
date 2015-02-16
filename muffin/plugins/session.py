import base64
import hashlib
import hmac
import time
import asyncio

import ujson as json

from . import BasePlugin


class SessionPlugin(BasePlugin):

    """ Support sessions. """

    name = 'session'
    defaults = {
        'secret': 'InsecureSecret',
    }

    def setup(self, app):
        """ Initialize the application. """
        super().setup(app)

        if self.options['secret'] == 'InsecureSecret':
            app.logger.warn('Use insecure secret key. Change AUTH_SECRET option in configuration.')

    @asyncio.coroutine
    def middleware_factory(self, app, handler):

        @asyncio.coroutine
        def middleware(request):
            request.session = Session(self.options['secret'])
            request.session.load(request.cookies)
            app.logger.debug('Started: %s', request.session)
            response = yield from handler(request)
            app.logger.debug('Ended: %s', request.session)
            request.session.save(response.set_cookie)
            return response
        return middleware


class Session(dict):

    encoding = 'UTF-8'

    def __init__(self, secret, key='session.id', **params):
        self.secret = secret
        self.key = key
        self.params = params
        self.store = {}

    def save(self, set_cookie):
        if set(self.store.items()) ^ set(self.items()):
            value = dict(self.items())
            value = json.dumps(value)
            value = self.encrypt(value)
            if not isinstance(value, str):
                value = value.encode(self.encoding)
            set_cookie(self.key, value, **self.params)

    def load(self, cookies, **kwargs):
        value = cookies.get(self.key, None)
        if value is None:
            return False
        data = json.loads(self.decrypt(value))
        if not isinstance(data, dict):
            return False
        self.store = data
        self.update(self.store)

    def create_signature(self, value, timestamp):
        h = hmac.new(self.secret.encode(), digestmod=hashlib.sha1)
        h.update(timestamp)
        h.update(value)
        return h.hexdigest()

    def encrypt(self, value):
        timestamp = str(int(time.time())).encode()
        value = base64.b64encode(value.encode(self.encoding))
        signature = self.create_signature(value, timestamp)
        return "|".join([value.decode(self.encoding), timestamp.decode(self.encoding), signature])

    def decrypt(self, value):
        value, timestamp, signature = value.split("|")
        check = self.create_signature(value.encode(self.encoding), timestamp.encode())
        if check != signature:
            return None
        return base64.b64decode(value).decode(self.encoding)
