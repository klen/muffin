import muffin


app = application = muffin.Application('example', CONFIG='example.config.debug')


from .admin import *  # noqa Initialize admin views
from .views import *  # noqa Initialize app views
from .manage import * # noqa Initialize app commands
