import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = 'postgresql://Manu:test@localhost:5432/test'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

