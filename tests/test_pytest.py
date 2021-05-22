import pytest


@pytest.fixture
def name(app):
    return app.cfg.name


async def test_app_imported(app, name):
    assert app.cfg.name == 'muffin'
    assert app.state == 'started'
