""" Peewee migrations. """

import datetime as dt
import peewee as pw


def migrate(migrator, database, **kwargs):
    """ Write your migrations here.

    > migrator.create_table(model)
    > migrator.drop_table(model, cascade=True)
    > migrator.add_columns(model, **fields)
    > migrator.drop_columns(models, *names, cascade=True)
    > migrator.rename_column(model, old_name, new_name)
    > migrator.rename_table(model, new_name)
    > migrator.add_index(model, *columns, unique=False)
    > migrator.drop_index(model, index_name)
    > migrator.add_not_null(model, name)
    > migrator.drop_not_null(model, name)

    """

    migrator.add_columns('user',
                         created=pw.DateTimeField(default=dt.datetime.now),
                         drop_me=pw.CharField(default=''))

    migrator.rename_column('user', 'drop_me', 'new_drop_me')

    migrator.add_index('user', 'new_drop_me')

    migrator.drop_columns('user', 'new_drop_me')
