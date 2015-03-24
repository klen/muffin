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

    import peewee as pw
    from muffin.plugins.peewee.migrate import Migrator

    migrator = Migrator(router.database)

    @migrator.create_table
    class Customer(pw.Model):
        name = pw.CharField()

    assert Customer == migrator.orm['customer']

    @migrator.create_table
    class Order(pw.Model):
        number = pw.CharField()

        customer = pw.ForeignKeyField(Customer)

    assert Order == migrator.orm['order']

    migrator.add_columns(Order, finished=pw.BooleanField(default=False))
    assert 'finished' in Order._meta.fields

    migrator.drop_columns('order', 'finished', 'customer')
    assert 'finished' not in Order._meta.fields

    migrator.add_columns(Order, customer=pw.ForeignKeyField(Customer, null=True))
    assert 'customer' in Order._meta.fields
