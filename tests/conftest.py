import pytest

import muffin


@pytest.fixture(scope='session')
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

    loop.run_until_complete(app.start())
    return app
