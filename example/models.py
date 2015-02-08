from peewee import * # noqa

from app import app


class Test(Model):

    data = CharField()

    class Meta(object):
        database = app.peewee.database


class Lama(Model):

    data = CharField()

    class Meta(object):
        database = app.peewee.database
