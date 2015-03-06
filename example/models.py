import peewee as pw
import datetime as dt

from muffin.plugins.peewee import PeeweePlugin
from muffin.utils import generate_password_hash, check_password_hash

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

    @property
    def pk(self):
        return self.id

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(password, self.password)
