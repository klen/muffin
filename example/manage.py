""" The application's commands. """

from example import app


@app.manage.command
def hello(name, upper=False):
    """ Write command help text here.

    :param name:  Write your name
    :param upper: Use uppercase

    """
    greetings = 'Hello %s!' % name
    if upper:
        greetings = greetings.upper()
    print(greetings)


@app.manage.command
def example_data():
    """ Create example users. """
    from mixer.backend.peewee import Mixer
    from muffin.utils import generate_password_hash
    from example.models import User

    mixer = Mixer(commit=True)
    mixer.guard(User.email == 'user@muffin.io').blend(
        User, email='user@muffin.io', password=generate_password_hash('pass'))
    mixer.guard(User.email == 'admin@muffin.io').blend(
        User, email='admin@muffin.io', password=generate_password_hash('pass'), is_super=True)
