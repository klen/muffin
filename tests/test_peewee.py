def test_query(client, mixer):
    mixer.blend('example.models.Test')

    response = client.get('/db-sync')
    assert response.json

    # response = client.get('/db-async')
    # assert response.json


def test_migrations(app, tmpdir):
    assert app.plugins.peewee.router

    router = app.plugins.peewee.router
    router.migrate_dir = str(tmpdir.mkdir('migrations'))

    assert not router.fs_migrations
    assert not router.db_migrations
    assert not router.diff

    # Create migration
    path = router.create('test')
    assert '000_test.py' in path
    assert router.fs_migrations
    assert not router.db_migrations
    assert router.diff

    # Run migrations
    router.run()
    assert router.db_migrations
    assert not router.diff

    path = router.create()
    assert '001_auto.py' in path
