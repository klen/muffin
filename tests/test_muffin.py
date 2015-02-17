""" Tests for `muffin` module. """

import pytest


def test_app(client):
    response = client.get('/')
    assert response.status_code == 200
    assert "Hello anonimous!" in response.text

    response = client.get('/404', status=404)
    assert response.status_code == 404

    response = client.get('/json')
    assert response.json
    assert response.json['json'] == 'here'


def test_static(client):
    response = client.get('/static/media.txt')
    assert response.status_code == 200
    assert response.content_type == 'text/plain'

    response = client.get('/static/unknow', status=404)
    assert '404' in response.text


def test_session(client, mixer):
    response = client.get('/')
    assert "Hello anonimous" in response.text

    response = client.get('/login?user=Mike')
    response = client.get('/')
    assert "Hello Mike" in response.text


def test_peewee(client, mixer):
    mixer.blend('models.Test')

    response = client.get('/db-sync')
    assert response.json

    # response = client.get('/db-async')
    # assert response.json


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
