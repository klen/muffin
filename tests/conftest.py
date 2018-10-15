import pytest

import muffin


@pytest.fixture
def app():
    app = muffin.Application(
        'muffin',

        STATIC_FOLDERS=(
            'tests/static1',
            'tests/static2',
        ))

    @app.register('/')
    def index(request):
        return 'OK'

    return app
