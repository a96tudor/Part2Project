import os


class Config(object):
    """
        Parent configuration class
    """
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = os.getenv('SECRET')
    DATABASE_HOST = '127.0.0.1'
    DATABASE_PORT = '27017'


class DevelopmentConfig(Config):
    """
        Development configuration class
    """
    DEBUG = True
    DATABASE_NAME = 'testing'


class TestingConfig(Config):
    """
        Testing configuration class
    """
    DEBUG = True
    DATABASE_NAME = 'testing'
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
    DATABASE_NAME = 'production'


APP_CONFIG = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig
}
