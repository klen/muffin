""" The application's models. """

import datetime as dt

import peewee as pw

from example import app
from muffin.utils import generate_password_hash, check_password_hash


@app.ps.peewee.register
class Test(pw.Model):

    """ A simple model. """

    data = pw.CharField()


@app.ps.peewee.register
class User(pw.Model):

    """ Implement application's users. """

    created = pw.DateTimeField(default=dt.datetime.now)
    username = pw.CharField()
    email = pw.CharField(unique=True)
    password = pw.CharField()
    is_super = pw.BooleanField(default=False)

    def __unicode__(self):
        return self.email

    @property
    def pk(self):
        return self.id

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(password, self.password)


@app.ps.peewee.register
class Token(pw.Model):

    """ Store OAuth tokens. """

    provider = pw.CharField()
    token = pw.CharField()
    token_secret = pw.CharField(null=True)

    user = pw.ForeignKeyField(User)

    class Meta:
        indexes = (('token', 'provider'), True),

    def __unicode__(self):
        return self.provider
