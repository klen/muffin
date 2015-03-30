# Gunicorn
# ========
bind = '127.0.0.1:5000'

# Muffin
# ======

PLUGINS = (
    'muffin.plugins.jade:JadePlugin',

    'muffin_peewee',
    'muffin_session',

    'invalid.plugin',
)

STATIC_ROOT = 'example/static'

# Plugin options
# ==============

AUTH_SECRET = 'SecretHere'
JADE_TEMPLATE_FOLDER = 'example/templates'
OAUTH2_CLIENTS = {
    'github': {
        'id': 'b6281b6fe88fa4c313e6',
        'secret': '21ff23d9f1cad775daee6a38d230e1ee05b04f7c',
    }
}
PEEWEE_MIGRATIONS_PATH = 'example/migrations'
