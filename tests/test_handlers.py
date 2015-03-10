def test_handler(client):
    response = client.get('/api/example')
    assert response.json
    assert not response.json['example']

    response = client.get('/api/example/1')
    assert response.json['example'] == '1'

    response = client.post('/api/example')
    assert response.json == [1, 2, 3]
