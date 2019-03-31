# import external libraries
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_moment import Moment
from flask_pagedown import PageDown


# local import
from config import config

# database variable db initialization
db = SQLAlchemy()
mail = Mail()
moment = Moment()
pagedown = PageDown()
login_manager = LoginManager()
login_manager.login_view = 'main.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    pagedown.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .lab import lab as lab_blueprint
    app.register_blueprint(lab_blueprint, url_prefix='/lab')

    from .users import users as users_blueprint
    app.register_blueprint(users_blueprint)

    from .errors import errors as errors_blueprint
    app.register_blueprint(errors_blueprint)

    return app
