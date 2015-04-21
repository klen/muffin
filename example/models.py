import datetime as dt

import peewee as pw

from example import app
from muffin.utils import generate_password_hash, check_password_hash


@app.ps.peewee.register
class Test(pw.Model):

    data = pw.CharField()


@app.ps.peewee.register
class Lama(pw.Model):

    data = pw.CharField()


@app.ps.peewee.register
class User(pw.Model):

    created = pw.DateTimeField(default=dt.datetime.now)
    username = pw.CharField()
    email = pw.CharField()
    password = pw.CharField()
    is_super = pw.BooleanField(default=False)

    @property
    def pk(self):
        return self.id

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(password, self.password)
