import os
from server.views import *


class Config(object):
    """
        Parent configuration class
    """
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = os.getenv('SECRET')

    TTL = 259200

    CACHE_CONN_DATA = {
        'host': '127.0.0.1',
        'port': 5432,
        'user': 'tma33',
        'password': 'password',
        'dbName': 'server-cache'
    }

    NEO4J_CONN_DATA = {
        'host': 'bolt://127.0.0.1',
        'port': 7687,
        'user': 'neo4j',
        'password': 'opus'
    }

    MODEL = {
        'name': 'pnn',
        'checkpoint': 'models/checkpoints/pnn'
    }

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
