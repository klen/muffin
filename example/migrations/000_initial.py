""" Peewee migrations. """

import datetime as dt
import peewee as pw


def migrate(migrator, app, database):
    """ Write your migrations here.

    > migrator.create_table(table, field_dict)
    > migrator.drop_table(table, cascade=True)
    > migrator.add_column(table, name, field)
    > migrator.drop_column(table, name, field, cascade=True)
    > migrator.rename_column(table, old_name, new_name)
    > migrator.rename_table(old_name, new_name)
    > migrator.add_index(table, columns, unique=False)
    > migrator.drop_index(table, index_name)
    > migrator.add_not_null(table, column)
    > migrator.drop_not_null(table, column)

    """
    migrator.create_table('user', {
        'created': pw.DateTimeField(default=dt.datetime.now),
        'username': pw.CharField(),
        'email': pw.CharField(),
        'password': pw.CharField(),
    })
