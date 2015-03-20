import pytest


def test_manage(app, capsys):
    @app.plugins.manage.command
    def hello(name, lower=False):
        if lower:
            name = name.lower()
        print("hello " + name)

    with pytest.raises(SystemExit):
        app.plugins.manage('example.app:app hello'.split())
    out, err = capsys.readouterr()
    assert not out
    assert err

    with pytest.raises(SystemExit):
        app.plugins.manage('example.app:app hello Mike'.split())
    out, err = capsys.readouterr()
    assert "hello Mike\n" == out

    with pytest.raises(SystemExit):
        app.plugins.manage('example.app:app hello Sam --lower'.split())
    out, err = capsys.readouterr()
    assert "hello sam\n" == out
