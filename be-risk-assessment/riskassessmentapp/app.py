from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from riskassessmentapp.extensions import db, bcrypt, mail
from flask_cors import CORS
from dotenv import load_dotenv
import os

def create_app():
    app = Flask(__name__, template_folder='templates')

    CORS(app)

    load_dotenv()

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # or any SMTP server
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_USERNAME")

    mail.init_app(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    app.secret_key = os.getenv("SECRET_KEY")

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    from riskassessmentapp.users.models import User

    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(uid)
    
    @login_manager.unauthorized_handler
    def unauthorized_callback():
        return "unauthorized"
    
    bcrypt = Bcrypt(app)

    from riskassessmentapp.users.routes import users
    app.register_blueprint(users, url_prefix='/users')
    from riskassessmentapp.search.routes import risksearch
    app.register_blueprint(risksearch, url_prefix='/risksearch')

    migrate = Migrate(app, db)

    return app

