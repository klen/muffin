import pytest


def test_manage(app, capsys):
    @app.plugins.manage.command
    def hello(name='Mike'):
        print("hello " + name)

    with pytest.raises(SystemExit):
        app.plugins.manage(['hello'])
    out, err = capsys.readouterr()
    assert "hello Mike\n" == out

    with pytest.raises(SystemExit):
        app.plugins.manage(['hello', '--name=Sam'])
    out, err = capsys.readouterr()
    assert "hello Sam\n" == out
