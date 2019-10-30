import environ

environ.Env.read_env('.env')

from .common import *

ALLOWED_HOSTS = ['localhost']
DEBUG = True
