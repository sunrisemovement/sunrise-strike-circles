import environ
import os

is_prod = os.environ.get('DJANGO_SETTINGS_MODULE') == 'sunrise.settings.production'
dirs_above = 4 if is_prod else 3  # The number of dirs above the current dir that the .env file is stored
root = environ.Path(__file__) - dirs_above

env = environ.Env(DEBUG=(bool, False),)
