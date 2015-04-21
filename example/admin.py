from muffin_admin.peewee import PWAdminHandler

from example import app
from example.models import User, Test, Token


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
