class PluginMeta(type):

    """ Ensure that each plugin is singleton. """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(PluginMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class BasePlugin(metaclass=PluginMeta):

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
