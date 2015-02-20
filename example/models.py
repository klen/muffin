from peewee import * # noqa

from muffin.plugins.peewee import PeeweePlugin

db = PeeweePlugin()


@db.register
class Test(Model):

    data = CharField()


@db.register
class Lama(Model):

    data = CharField()
