import muffin


app = application = muffin.Application('example', CONFIG='example.config.debug')


from .views import *  # noqa Import views
from .manage import * # noqa Import commands
