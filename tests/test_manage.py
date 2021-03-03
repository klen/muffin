import pytest
from unittest import mock


def test_command(app):

    @app.manage
    def cmd1(name, lower=False):
        """Custom description.

        :param name: help for name
        """
        pass

    assert cmd1.parser
    assert cmd1.parser.description == 'Custom description.'
    assert cmd1.parser._actions[1].help == 'help for name'
    ns = cmd1.parser.parse_args(['test'])
    assert dict(ns._get_kwargs()) == {'name': 'test', 'lower': False}

    @app.manage
    def cmd2(*names, lower=False):
        pass

    ns = cmd2.parser.parse_args(['test'])
    assert dict(ns._get_kwargs()) == {'*': ['test'], 'lower': False}


def test_manage(app, capsys, monkeypatch):

    start = mock.MagicMock()
    app.on_startup(start)

    finish = mock.MagicMock()
    app.on_shutdown(finish)

    @app.manage(lifespan=True)
    def hello(user_name, lower=False):
        if lower:
            user_name = user_name.lower()
        print("hello " + user_name)

    with pytest.raises(SystemExit):
        app.manage.run(*'hello')

    out, err = capsys.readouterr()
    assert not out
    assert err

    with pytest.raises(SystemExit):
        app.manage.run(*'hello Mike'.split())

    assert start.called
    assert finish.called

    out, err = capsys.readouterr()
    assert "hello Mike\n" == out

    with pytest.raises(SystemExit):
        app.manage.run(*'hello Sam --lower'.split())

    out, err = capsys.readouterr()
    assert "hello sam\n" == out


def test_manage_async(app):

    EVENTS = {}

    @app.manage
    async def command():
        EVENTS['command'] = True

    with pytest.raises(SystemExit) as excinfo:
        app.manage.run('command')

    assert excinfo.value.code == 0
    assert EVENTS['command']

