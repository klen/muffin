class BasePlugin:

    """ Implement base plugin functionality. """

    name = 'base'
    defaults = {}

    def __init__(self, **options):
        self.app = None
        self.options = options

    def setup(self, app):
        """ Initialize the application. """
        self.app = app
        for key in self.defaults:
            name = ('%s_%s' % (self.name, key)).upper()
            app.config.setdefault(name, self.defaults[key])
            self.options.setdefault(key, app.config[name])
