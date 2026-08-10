from unittest import mock

import muffin


def test_configure_logging():
    dummy = {"dummy": "dict", "version": 1}
    with mock.patch("muffin.app.dictConfig") as mocked:
        app = muffin.Application("muffin", LOG_CONFIG=dummy)
        assert app.logger
        assert app.logger.handlers
    mocked.assert_called_once_with(dummy)
