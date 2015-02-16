import asyncio

from gunicorn.app.base import Application as VanillaGunicornApp
from gunicorn.workers.base import Worker as VanillaGunicornWorker


class GunicornApp(VanillaGunicornApp):

    """ Support Gunicorn. """

    def __init__(self, app, *args, **kwargs):
        super(GunicornApp, self).__init__(*args, **kwargs)
        self.app = app
        self.cfg.set('worker_class', 'muffin.worker.GunicornWorker')
        self.cfg.set('reload', True)

    def load_config(self):
        pass

    def load(self):
        return self.app


class GunicornWorker(VanillaGunicornWorker):

    """ Class description. """

    def __init__(self, *args, **kwargs):
        super(GunicornWorker, self).__init__(*args, **kwargs)
        self.servers = {}

    def init_process(self):
        # create new event_loop after fork
        asyncio.get_event_loop().close()

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        super().init_process()

    def run(self):
        container = self.app.callable
        container._loop = self.loop
        container.loop.set_debug(container.config['DEBUG'])
        handler = container.make_handler()
        for i, sock in enumerate(self.sockets):
            srv = self.loop.run_until_complete(self.loop.create_server(handler, sock=sock.sock))
            self.servers[srv] = handler

        self.notify()
        self.loop.run_forever()

    def notify(self):
        super(GunicornWorker, self).notify()
        self.loop.call_later(self.timeout, self.notify)
