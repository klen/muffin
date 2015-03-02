import asyncio
import concurrent
import threading

import peewee


class AsyncDatabaseMixin:

    max_connections = 4

    def __init__(self, database, loop=None, **kwargs):
        self.connections = {}
        super().__init__(database, **kwargs)
        self.loop = loop or asyncio.get_event_loop()
        self.threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_connections)

    @property
    def _Database__local(self):
        tid = threading.get_ident()
        return self.connections.get(tid, peewee._ConnectionLocal())

    @_Database__local.setter
    def _Database__local(self, value):
        tid = threading.get_ident()
        self.connections[tid] = value
