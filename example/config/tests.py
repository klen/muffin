# Import the project's settings
from .production import *

PEEWEE_CONNECTION = 'sqlite:///:memory:'
PEEWEE_MAX_CONNECTIONS = 1
