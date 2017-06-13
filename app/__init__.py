from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    # 初始化配置
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 注册方法
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .manage import manage as manage_blueprint
    app.register_blueprint(manage_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .api_v1 import api_v1 as api_v1_blueprint
    app.register_blueprint(api_v1_blueprint, url_prefix='/api_v1')

    from .form import form as form_blueprint
    app.register_blueprint(form_blueprint)
    # 注册蓝图

    return app
