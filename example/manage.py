""" Application's manage commands. """

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
