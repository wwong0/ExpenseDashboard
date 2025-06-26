from flask import Blueprint, jsonify
from flask_jwt_extended import create_access_token
from flask_pydantic import validate

from validation_schemas.schemas import AuthSchema
from services import auth_service, NotFoundError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@validate()
def register(body: AuthSchema):

    new_user = auth_service.register_user(data = body)

    access_token = create_access_token(identity=new_user.id)

    return jsonify(access_token=access_token), 201

@auth_bp.route('/login', methods=['POST'])
@validate()
def login(body: AuthSchema):
    user = auth_service.login_user(data = body)

    access_token = create_access_token(identity=user.id)

    return jsonify(access_token=access_token), 200

