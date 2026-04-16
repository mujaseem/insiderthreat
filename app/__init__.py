from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))


def create_app():

    app = Flask(__name__)

    app.config.from_object("config.Config")

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Import models
    from app.models.user import User
    from app.models.log import Log
    from app.models.threat import Threat
    from app.models.alert import Alert
    from app.models.blockchain_block import BlockchainBlock   # ✅ Added line

    # Import routes
    from app.routes.auth_routes import auth
    from app.routes.dashboard_routes import dashboard_bp

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(dashboard_bp)

    return app