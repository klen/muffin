from unittest import mock

import pytest

import muffin.manage as manage_module
from muffin.utils import current_async_library


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


def test_command_bool_true_and_list_defaults(app):
    @app.manage
    def command(*, enabled=True, tags=["base"]):  # noqa: B006
        pass

    ns = command.parser.parse_args("--no-enabled --tags extra".split())  # type: ignore[]
    assert dict(ns._get_kwargs()) == {
        "enabled": False,
        "tags": ["base", "extra"],
    }


def test_manage_variadic_command_ignores_kwargs(app):
    called = mock.MagicMock()

    @app.manage
    def collect(*items, **options):
        called(items, options)

    app.manage.run(*"collect one two".split())
    called.assert_called_once_with(("one", "two"), {})


def test_cli_success(monkeypatch):
    fake_manage = mock.MagicMock()
    fake_logger = mock.MagicMock()
    fake_app = mock.MagicMock(logger=fake_logger, manage=fake_manage)
    fake_app.cfg.name = "demo"

    monkeypatch.setattr(manage_module, "import_app", lambda _: fake_app)
    monkeypatch.setenv(manage_module.CONFIG_ENV_VARIABLE, "")
    monkeypatch.setattr(
        manage_module.sys,
        "argv",
        ["muffin", "project.app", "--config", "config.toml", "hello", "Mike"],
    )

    with pytest.raises(SystemExit) as exc_info:
        manage_module.cli()

    assert exc_info.value.code == 0
    assert fake_manage.run.call_args == mock.call("hello", "Mike", prog="muffin project.app")
    assert manage_module.os.environ[manage_module.CONFIG_ENV_VARIABLE] == "config.toml"


def test_cli_import_error(monkeypatch):
    monkeypatch.setattr(
        manage_module,
        "import_app",
        mock.MagicMock(side_effect=ImportError("broken app")),
    )
    monkeypatch.setattr(manage_module.sys, "argv", ["muffin", "broken.app"])

    with pytest.raises(SystemExit) as exc_info:
        manage_module.cli()

    assert exc_info.value.code == 1
