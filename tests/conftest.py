import pytest

import muffin


@pytest.fixture
def app(loop):
    app = muffin.Application(
        'muffin', loop=loop,

        PLUGINS=(
            'invalid.plugin',
        ),

        STATIC_FOLDERS=(
            'tests/static1',
            'tests/static2',
        ))

    @app.register('/')
    def index(request):
        return 'OK'

    return app
