import pytest
import mock


def test_command(app):

    @app.manage.command
    def cmd1(name, lower=False):
        pass

    assert cmd1.parser
    ns = cmd1.parser.parse_args(['test'])
    assert dict(ns._get_kwargs()) == {'name': 'test', 'lower': False}

    @app.manage.command
    def cmd2(*names, lower=False):
        pass

    ns = cmd2.parser.parse_args(['test'])
    assert dict(ns._get_kwargs()) == {'*': ['test'], 'lower': False}


def test_manage(app, capsys, monkeypatch):

    def startup(*args):
        raise Exception('must not be called')

    monkeypatch.setattr(app, 'startup', startup)

    @app.manage.command(init=False)
    def hello(name, lower=False):
        if lower:
            name = name.lower()
        print("hello " + name)

    with pytest.raises(SystemExit):
        app.manage(*'hello'.split())

    out, err = capsys.readouterr()
    assert not out
    assert err

    with pytest.raises(SystemExit):
        app.manage(*'hello Mike'.split())
    out, err = capsys.readouterr()
    assert "hello Mike\n" == out

    with pytest.raises(SystemExit):
        app.manage(*'hello Sam --lower'.split())
    out, err = capsys.readouterr()
    assert "hello sam\n" == out

