from flask import Flask
from .config import Config
from .extensions import db, login_manager
from .auth.routes import auth_bp
from .main.routes import main_bp




def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app
