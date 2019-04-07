import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:

    """
    Common configuration settings
    """
    # general config
    SECRET_KEY = os.environ.get('SECRET_KEY')
    LAB_ADMIN = os.environ.get('LAB_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # smtp/email config
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))
    MAIL_USE_TLS = True
    MAIL_SUBJECT = os.environ.get('MAIL_SUBJECT_HEMOGRAM')
    MAIL_SENDER = os.environ.get('MAIL_SENDER_HEMOGRAM')

    # files storage config
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY_ID = os.environ.get('AWS_SECRET_ACCESS_KEY_ID')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):

    """
    Development enviroment configuration
    """

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URI')


class TestingConfig(Config):
    """
    Testing enviroment configuration
    """

    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')


class ProductionConfig(Config):

    """
    Production enviroment configuration
    """
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
