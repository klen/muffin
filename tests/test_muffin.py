""" Tests for `muffin` module. """


def test_app(client):
    response = client.get('/')
    assert response.status_code == 200
    assert "Hello world!" in response.text

    response = client.get('/404', status=404)
    assert response.status_code == 404

    response = client.get('/json')
    assert response.json
    assert response.json['json'] == 'here'

    response = client.get('/db-sync')
    assert response.json

    response = client.get('/db-async')
    assert response
