import pytest


@pytest.fixture()
def name(app):
    return app.cfg.name


def test_app_imported(app):
    assert app.cfg.name == "muffin"


def test_app_available_in_fixture(name):
    assert name == "muffin"


def test_app_lifespan(app):
    assert app.state == "started"
