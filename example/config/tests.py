# Import the project's settings
from config.production import *

PEEWEE_CONNECTION = 'sqlite:///:memory:'
PEEWEE_MAX_CONNECTIONS = 1
