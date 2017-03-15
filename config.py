import os


class Config:
    # Pull SECRET_KEY from environment variable, as God meant it to be :)
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    WEATHER_APP_MAIL_SUBJECT_PREFIX = '[WEATHER_APP]'
    WEATHER_APP_MAIL_SENDER = 'WEATHER_APP Admin <weather_app@example.com>'
    WEATHER_APP_ADMIN = os.environ.get('WEATHER_APP_ADMIN')

    OWM_API_KEY = os.environ.get('OWM_API_KEY')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('WEATHER_APP_DEV_DB') or 'postgresql://tom:tom@localhost/weather_app'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('WEATHER_APP_TEST_DB') or 'postgresql://tom:tom@localhost/weather_app_testing'
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('WEATHER_APP_PROD_DB')


config = {
    'default': DevelopmentConfig,

    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
