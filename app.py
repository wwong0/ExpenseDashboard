from flask import Flask, jsonify
from flask_jwt_extended import JWTManager

from config import Config
from models import db
from routes import auth_bp, expense_bp, income_bp, budget_bp
from services import NotFoundError
from services.auth_service import UserAlreadyExistsError, InvalidCredentialError
from services.budget_service import BudgetAlreadyExistsError
from utils.json_provider import PydanticJSONProvider

def create_app(config_class = Config):
    """
    Creates and configures a new Flask application instance.
    This function follows the Application Factory pattern.

    Args:
        config_class: The configuration class to use for the app.
                      Defaults to the production Config.

    Returns:
        The configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.json = PydanticJSONProvider(app)

    jwt = JWTManager(app)
    db.init_app(app)

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(expense_bp, url_prefix='/api')
    app.register_blueprint(income_bp, url_prefix='/api')
    app.register_blueprint(budget_bp, url_prefix='/api')


    @app.errorhandler(NotFoundError)
    def handle_not_found(error):
        """Handles NotFoundError across the entire application."""
        response = jsonify({"error": str(error)})
        response.status_code = 404
        return response


    @app.errorhandler(UserAlreadyExistsError)
    def handle_user_already_exists(error):
        response = jsonify({"error": str(error)})
        response.status_code = 409 # 409 Conflict
        return response

    @app.errorhandler(InvalidCredentialError)
    def handle_invalid_credentials(error):
        response = jsonify({"error": str(error)})
        response.status_code = 401 # 401 Unauthorized
        return response

    @app.errorhandler(BudgetAlreadyExistsError)
    def hande_budget_already_exists(error):
        response = jsonify({"error": str(error)})
        response.status_code = 409
        return response


    return app
