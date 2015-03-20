import pytest


def test_manage(app, capsys):
    @app.plugins.manage.command
    def hello(name='Mike'):
        print("hello " + name)

    with pytest.raises(SystemExit):
        app.plugins.manage(['example.app:app', 'hello'])
    out, err = capsys.readouterr()
    assert "hello Mike\n" == out

    with pytest.raises(SystemExit):
        app.plugins.manage(['example.app:app', 'hello', '--name=Sam'])
    out, err = capsys.readouterr()
    assert "hello Sam\n" == out
