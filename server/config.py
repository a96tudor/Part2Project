import os
from server.views import *


class Config(object):
    """
        Parent configuration class
    """
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = os.getenv('SECRET')

    CACHE_DATABASE_HOST = 'http://127.0.0.1'
    CACHE_DATABASE_PORT = 1234
    CACHE_DATABASE_USER = 'cadets'
    CACHE_DATABASE_PASS = 'pass'

    FEATURES_DATABASE_HOST = 'bolt://127.0.0.1'
    FEATURES_DATABASE_PORT = 7687
    FEATURES_DATABASE_USER = 'neo4j'
    FEATURES_DATABASE_PASS = 'opus'

    MODEL = 'mlp'

    views = [
        {
            'url': '/classify',
            'class': ClassifyView
        },
        {
            'url': '/clear-cache',
            'class': CacheResetView
        },
        {
            'url': '/db-connect',
            'class': Neo4JConnectView
        },
        {
            'url': '/job-action',
            'class': JobActionView
        }
    ]


class DevelopmentConfig(Config):
    """
        Development configuration class
    """
    DEBUG = True
    CACHE_DATABASE_NAME = 'testing'


class TestingConfig(Config):
    """
        Testing configuration class
    """
    DEBUG = True
    CACHE_DATABASE_NAME = 'testing'
    TESTING = True


class StagingConfig(Config):
    """
        Staging configuration class
    """
    DEBUG = True
    DATABASE_NAME = 'testing'


class ProductionConfig(Config):
    """
        Production configuration class
    """
    DEBUG = False
    CACHE_DATABASE_NAME = 'production'
    TESTING = False


APP_CONFIG = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig
}
