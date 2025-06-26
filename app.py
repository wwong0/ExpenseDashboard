from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from routes import auth_bp, expense_bp
from services import NotFoundError
from services.auth_service import UserAlreadyExistsError, InvalidCredentialError

app = Flask(__name__)
app.config.from_object(Config)
jwt = JWTManager(app)

db.init_app(app)
app.register_blueprint(auth_bp)
app.register_blueprint(expense_bp)

@app.errorhandler(NotFoundError)
def handle_not_found(error):
    """Handles NotFoundError across the entire application."""
    response = jsonify({"error": str(error)})
    response.status_code = 404
    return response

@app.errorhandler(ValueError)
def handle_value_error(error):
    """Handles ValueError for things like invalid IDs from the service layer."""
    response = jsonify({"error": str(error)})
    response.status_code = 400
    return response

@app.errorhandler(UserAlreadyExistsError)
def handle_user_already_exists(error):
    response = jsonify({"error": str(error)})
    response.status_code = 409
    return response

@app.errorhandler(InvalidCredentialError)
def handle_invalid_credentials(error):
    response = jsonify({"error": str(error)})
    response.status_code = 401
    return response

@app.route('/')
def home():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
