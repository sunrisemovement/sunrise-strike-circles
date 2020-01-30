import environ

environ.Env.read_env('.env')

from .common import *

ALLOWED_HOSTS = ['localhost'] + env.list('SITE_URLS')
DEBUG = False
