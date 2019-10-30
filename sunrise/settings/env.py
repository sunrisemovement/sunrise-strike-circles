import environ

root = environ.Path(__file__) - 3  # Three folders up
env = environ.Env(DEBUG=(bool, False),)
