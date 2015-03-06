""" Tests for `muffin` module. """


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
    response = client.get('/static/app.css')
    assert response.status_code == 200
    assert response.content_type == 'text/css'

    response = client.get('/static/unknow', status=404)
    assert '404' in response.text


def test_login_logout(client, mixer):
    response = client.get('/')
    assert "Hello anonimous" in response.text

    from muffin.utils import generate_password_hash
    user = mixer.blend('example.models.User', password=generate_password_hash('pass'))
    response = client.post('/login', params={'email': user.email, 'password': 'pass'})
    assert response.status_code == 302

    response = client.get('/')
    assert "Hello %s" % user.username in response.text

    response = client.get('/logout')
    assert response.status_code == 302

    response = client.get('/')
    assert "Hello anonimous" in response.text
