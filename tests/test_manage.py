import pytest
from unittest import mock


def test_command(app):

    @app.manage
    def cmd1(name, lower=False):
        pass

    assert cmd1.parser
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
    def hello(name, lower=False):
        if lower:
            name = name.lower()
        print("hello " + name)

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
