""" Admin interface. """

import muffin
from muffin_admin.peewee import PWAdminHandler

from example import app
from example.models import User, Test, Token


@app.ps.admin.authorization
def authorize(request):
    """ Check for current user's permissions.

    Can be redifined for each handler.

    """
    user = yield from app.ps.session.load_user(request)
    if not user or not user.is_super:
        raise muffin.HTTPFound('/')
    return user


@app.register
class UserAdmin(PWAdminHandler):
    model = User
    columns = 'id', 'created', 'username', 'email', 'is_super'
    form_meta = {
        'exclude': ['password'],
    }


@app.register
class TokenAdmin(PWAdminHandler):
    model = Token


@app.register
class TestAdmin(PWAdminHandler):
    model = Test
