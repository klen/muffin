from unittest import mock

import pytest


@pytest.fixture(params=["curio", "trio", "asyncio"])
def cmd_aiolib(request):
    return request.param


def test_command(app):
    @app.manage
    def cmd1(name, *, lower=False):
        """Custom description.

        :param name: help for name
        """

    parser = cmd1.parser  # type: ignore[]
    assert parser
    assert parser.description == "Custom description."
    assert parser._actions[1].help == "help for name"
    ns = parser.parse_args(["test"])
    assert dict(ns._get_kwargs()) == {"name": "test", "lower": False}

    @app.manage
    def cmd2(*names, lower=False):
        pass

    ns = cmd2.parser.parse_args(["test"])  # type: ignore[]
    assert dict(ns._get_kwargs()) == {"names": ["test"], "lower": False}


def test_manage(app, capsys, monkeypatch):
    @app.manage
    def hello(user_name, *, lower=False):
        if lower:
            user_name = user_name.lower()
        print("hello " + user_name)

    with pytest.raises(SystemExit):
        app.manage.run(*"hello")

    out, err = capsys.readouterr()
    assert not out
    assert err

    app.manage.run(*"hello Mike".split())

    out, err = capsys.readouterr()
    assert "hello Mike\n" == out

    app.manage.run(*"hello Sam --lower".split())

    out, err = capsys.readouterr()
    assert "hello sam\n" == out


def test_manage_async(app, cmd_aiolib):
    import typing as t

    from muffin.utils import current_async_library

    start = mock.MagicMock()
    app.on_startup(start)

    finish = mock.MagicMock()
    app.on_shutdown(finish)

    run = mock.MagicMock()

    @app.manage(lifespan=True)
    async def command(name: str | int):
        run(name)
        assert current_async_library() == cmd_aiolib

    app.manage.run(*f"--aiolib={cmd_aiolib} command test".split())
    assert run.called
    args, _ = run.call_args
    assert args == ("test",)
    assert start.called
    assert finish.called


def test_shell_context(app):
    assert app.cfg.MANAGE_SHELL

    @app.manage.shell
    def custom_context():
        return {"custom": True}

    assert app.cfg.MANAGE_SHELL is custom_context
