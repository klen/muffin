import peewee as pw
import datetime as dt

from muffin.plugins.peewee import PeeweePlugin

db = PeeweePlugin()


@db.register
class Test(pw.Model):

    data = pw.CharField()


@db.register
class Lama(pw.Model):

    data = pw.CharField()


@db.register
class User(pw.Model):

    created = pw.DateTimeField(default=dt.datetime.now)
    username = pw.CharField()
    email = pw.CharField()
    password = pw.CharField()
