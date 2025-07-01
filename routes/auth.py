from flask import Blueprint, jsonify
from flask_jwt_extended import create_access_token
from flask_pydantic import validate

from validation_schemas.schemas import AuthSchema
from services import auth_service

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@validate()
def register(body: AuthSchema):
    """Registers a new user.

    Args:
        body: The user's credentials (username, password) validated by
            Pydantic.

    Returns:
        A JSON object containing the JWT access token and a 201 Created status.
    """
    new_user = auth_service.register_user(data=body)
    access_token = create_access_token(identity=new_user.id)
    return jsonify(access_token=access_token), 201


@auth_bp.route('/login', methods=['POST'])
@validate()
def login(body: AuthSchema):
    """Logs in an existing user.

    Args:
        body: The user's credentials (username, password) validated by
            Pydantic.

    Returns:
        A JSON object containing the JWT access token and a 200 OK status.
    """
    user = auth_service.login_user(data=body)
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200