import datetime as dt
from cached_property import cached_property
from os import path as op, listdir as ls, makedirs as md
from re import compile as re
from shutil import copy

import peewee as pw
from playhouse.migrate import SchemaMigrator


MIGRATE_TEMPLATE = op.join(
    op.abspath(op.dirname(__file__)), 'migration.tmpl'
)


def exec_in(codestr, glob, loc=None):
    code = compile(codestr, '<string>', 'exec', dont_inherit=True)
    exec(code, glob, loc)


class MigrationError(Exception):

    """ Presents an error during migration process. """


class Router(object):

    """ Control migrations. """

    filemask = re(r"[\d]{3}_[^\.]+\.py")

    def __init__(self, plugin):
        self.app = plugin.app
        self.database = plugin.database
        self.migrate_dir = plugin.options['migrations_path']
        if not op.exists(self.migrate_dir):
            self.app.logger.warn('Migration directory: %s does not exists.', self.migrate_dir)
            md(self.migrate_dir)

    @cached_property
    def model(self):
        """ Ensure that migrations has prepared to run. """
        # Initialize MigrationHistory model
        MigrateHistory._meta.database = self.app.plugins.peewee.database
        try:
            MigrateHistory.create_table()
        except pw.OperationalError:
            pass
        return MigrateHistory

    @property
    def fs_migrations(self):
        return sorted(''.join(f[:-3]) for f in ls(self.migrate_dir) if self.filemask.match(f))

    @property
    def db_migrations(self):
        return [mm.name for mm in self.model.select()]

    @property
    def diff(self):
        db = set(self.db_migrations)
        return [name for name in self.fs_migrations if name not in db]

    def create(self, name='auto'):
        """ Create a migration. """

        self.app.logger.info('Create a migration "%s"', name)

        num = len(self.fs_migrations)
        prefix = '{:03}_'.format(num)
        name = prefix + name + '.py'
        path = copy(MIGRATE_TEMPLATE, op.join(self.migrate_dir, name))

        self.app.logger.info('Migration has created %s', path)
        return path

    def run(self, name=None):
        """ Run migrations. """

        self.app.logger.info('Start migrations')

        migrator = Migrator(self.database)
        if name:
            return self.run_one(name, migrator)

        diff = self.diff
        for name in diff:
            self.run_one(name, migrator)

        if not diff:
            self.app.logger.info('Nothing to migrate')

    def run_one(self, name, migrator):
        """ Run a migration. """

        self.app.logger.info('Run "%s"', name)

        try:
            with open(op.join(self.migrate_dir, name + '.py')) as f:
                with self.database.transaction():
                    code = f.read()
                    scope = {}
                    exec_in(code, scope)
                    migrate = scope.get('migrate', lambda m: None)
                    self.app.logger.info('Start migration %s', name)
                    migrate(migrator, self.app, self.database)
                    self.model.create(name=name)
                    self.app.logger.info('Migrated %s', name)

        except Exception as exc:
            self.database.rollback()
            self.app.logger.error(exc)


class MigrateHistory(pw.Model):

    """ Presents the migrations in database. """

    name = pw.CharField()
    migrated_at = pw.DateTimeField(default=dt.datetime.utcnow)


class Migrator(object):

    """ Provide migrations. """

    def __init__(self, db):
        self.db = db
        self.orm = dict()
        self.migrator = SchemaMigrator.from_database(self.db)

    def create_table(self, table, fields):
        model = type(table, (pw.Model,), fields)
        self.db.create_table(model)

    def drop_table(self, table, cascade=True):
        class model(pw.Model):
            class Meta:
                db_table = table
        return self.db.drop_table(model, cascade=cascade)

    def add_column(self, table, name, field):
        operation = self.migrator.add_column(table, name, field)
        return operation.run()

    def drop_column(self, table, name, field, cascade=True):
        operation = self.migrator.drop_column(table, name, field, cascade=cascade)
        return operation.run()

    def rename_column(self, table, old_name, new_name):
        operation = self.migrator.rename_column(table, old_name, new_name)
        return operation.run()

    def rename_table(self, old_name, new_name):
        operation = self.migrator.rename_table(old_name, new_name)
        return operation.run()

    def add_index(self, table, columns, unique=False):
        operation = self.migrator.add_index(table, columns, unique=unique)
        return operation.run()

    def drop_index(self, table, index_name):
        operation = self.migrator.drop_index(table, index_name)
        return operation.run()

    def add_not_null(self, table, column):
        operation = self.migrator.add_not_null(table, column)
        return operation.run()

    def drop_not_null(self, table, column):
        operation = self.migrator.drop_not_null(table, column)
        return operation.run()
