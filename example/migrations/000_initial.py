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

    @migrator.create_table
    class User(pw.Model):
        username = pw.CharField()
        email = pw.CharField(unique=True)
        password = pw.CharField()
        is_super = pw.BooleanField(default=False)

    @migrator.create_table
    class Test(pw.Model):
        data = pw.CharField()

    @migrator.create_table
    class Token(pw.Model):
        provider = pw.CharField()
        token = pw.CharField()
        token_secret = pw.CharField(null=True)
        user = pw.ForeignKeyField(User)

        class Meta:
            indexes = (('token', 'provider'), True),
