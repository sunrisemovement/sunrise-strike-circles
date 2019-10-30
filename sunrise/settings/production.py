import environ

environ.Env.read_env('.env')

from .common import *

DEBUG = False
ALLOWED_HOSTS = ['localhost']
