from peewee import * # noqa

from muffin.plugins.peewee import PeeweePlugin

db = PeeweePlugin()


class Test(Model):

    data = CharField()

    class Meta(object):
        database = db.database


class Lama(Model):

    data = CharField()

    class Meta(object):
        database = db.database
