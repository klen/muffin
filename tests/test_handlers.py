def test_handler(client):
    response = client.get('/api/example')
    assert response.json
    assert not response.json['example']

    response = client.get('/api/example/1')
    assert response.json['example'] == '1'

    response = client.post('/api/example')
    assert response.json == [1, 2, 3]

    response = client.delete('/api/example', status=405)
    assert response.status_code == 405


def test_sre(app):
    from muffin import sre

    re = sre('/test/{id:\d+}/?')
    assert re.match('/test/1')
    assert re.match('/test/2/')

    re = sre('/test/{id:\d+}/{name}/?')
    assert re.match('/test/1/Mike')

    re = sre('/test(/{id}/?)?')
    assert re.match('/test/')
    assert re.match('/test/1')
    assert re.match('/test/1/').group('id') == '1'
