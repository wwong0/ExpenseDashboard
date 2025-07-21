from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_pydantic import validate

from services import income_service
from validation_schemas.schemas import CreateIncomeSchema, UpdateIncomeSchema, IncomeResponseSchema
from utils.route_utils import pagination_to_response_data

income_bp = Blueprint('incomes', __name__)

@income_bp.route('/incomes', methods=['POST'])
@jwt_required()
@validate()
def create_income(body: CreateIncomeSchema):
    """Creates a new income record for the authenticated user."""
    user_id = get_jwt_identity()
    new_income = income_service.create_income(user_id=user_id, data=body)
    response_data = IncomeResponseSchema.model_validate(new_income)
    return response_data.model_dump(), 201

@income_bp.route('/incomes', methods=['GET'])
@jwt_required()
def get_all_incomes():
    """Retrieves all incomes for the authenticated user."""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = income_service.get_all_incomes(user_id, page=page, per_page=per_page)
    response_data = pagination_to_response_data(pagination, IncomeResponseSchema)
    return jsonify(response_data), 200

@income_bp.route('/incomes/<int:income_id>', methods=['GET'])
@jwt_required()
def get_income(income_id: int):
    """Retrieves a single income by its ID."""
    user_id = get_jwt_identity()
    income = income_service.get_income_by_id(user_id, income_id)
    response_data = IncomeResponseSchema.model_validate(income)
    return response_data.model_dump(), 200

@income_bp.route('/incomes/<int:income_id>', methods=['PUT'])
@jwt_required()
@validate()
def update_income(income_id: int, body: UpdateIncomeSchema):
    """Updates an existing income."""
    user_id = get_jwt_identity()
    income = income_service.update_income(user_id=user_id, income_id=income_id, data=body)
    response_data = IncomeResponseSchema.model_validate(income)
    return response_data.model_dump(), 200

@income_bp.route('/incomes/<int:income_id>', methods=['DELETE'])
@jwt_required()
def delete_income(income_id: int):
    """Deletes an income by its ID."""
    user_id = get_jwt_identity()
    income_service.delete_income(user_id=user_id, income_id=income_id)
    return '', 204