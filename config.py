import os
basedir = os.path.abspath(os.path.dirname(__file__))
# postgresql://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    # PG_DB = os.environ['PG_DB']
    # PG_USER = os.environ['PG_USER']
    # PG_PASS = os.environ['PG_PASSWORD']
    # SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL'].format(PG_USER, PG_PASS, PG_DB)


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

    def __str__(self):
        return f'{self.DEBUG}, {self.SQLALCHEMY_DATABASE_URI}'


class TestingConfig(Config):
    TESTING = True