PLUGINS = (
    'muffin.plugins.manage:ManagePlugin',
    'muffin.plugins.jade:JadePlugin',
    'muffin.plugins.peewee:PeeweePlugin',
    'muffin.plugins.session:SessionPlugin',

    'invalid.plugin',
)

# Plugin options
# ==============

AUTH_SECRET = 'SecretHere'
JADE_TEMPLATE_FOLDER = 'example/templates'
