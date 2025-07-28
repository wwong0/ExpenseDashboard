from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_pydantic import validate

from services import budget_service
from validation_schemas.schemas import CreateBudgetSchema, UpdateBudgetSchema, BudgetResponseSchema
from utils.route_utils import pagination_to_response_data

budget_bp = Blueprint('budgets', __name__)

@budget_bp.route('/budgets', methods=['POST'])
@jwt_required()
@validate()
def create_budget(body: CreateBudgetSchema):
    """Creates a new budget for the authenticated user."""
    user_id = get_jwt_identity()
    new_budget = budget_service.create_budget(user_id=user_id, data=body)
    response_data = BudgetResponseSchema.model_validate(new_budget)
    return response_data.model_dump(), 201

@budget_bp.route('/budgets', methods=['GET'])
@jwt_required()
def get_all_budgets():
    """Retrieves all budgets for the authenticated user."""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = budget_service.get_all_budgets(user_id, page=page, per_page=per_page)
    response_data = pagination_to_response_data(pagination, BudgetResponseSchema)
    return jsonify(response_data), 200

@budget_bp.route('/budgets/<int:budget_id>', methods=['GET'])
@jwt_required()
def get_budget(budget_id: int):
    """Retrieves a single budget by its ID."""
    user_id = get_jwt_identity()
    budget = budget_service.get_budget_by_id(user_id, budget_id)
    response_data = BudgetResponseSchema.model_validate(budget)
    return response_data.model_dump(), 200


@budget_bp.route('/budgets/summary', methods=['GET'])
@jwt_required()
def get_budget_summary_for_month():
    """
    Retrieves a structured summary of all budgets for a given month and year.
    This includes the overall budget (if set) and a list of all
    categorical budgets.

    Query Params:
        year (int): The year to retrieve budgets for.
        month (int): The month (1-12) to retrieve budgets for.

    Returns:
        A JSON object containing the structured budget summary.
    """
    user_id = get_jwt_identity()

    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    if not year or not month:
        return jsonify({"error": "Both 'year' and 'month' query parameters are required."}), 400

    if not (1 <= month <= 12):
        return jsonify({"error": "'month' must be an integer between 1 and 12."}), 400

    budget_summary = budget_service.get_budget_by_year_month(
        user_id=user_id,
        year=year,
        month=month
    )

    return jsonify(budget_summary), 200

@budget_bp.route('/budgets/<int:budget_id>', methods=['PUT'])
@jwt_required()
@validate()
def update_budget(budget_id: int, body: UpdateBudgetSchema):
    """Updates an existing budget."""
    user_id = get_jwt_identity()
    budget = budget_service.update_budget(user_id=user_id, budget_id=budget_id, data=body)
    response_data = BudgetResponseSchema.model_validate(budget)
    return response_data.model_dump(), 200

@budget_bp.route('/budgets/<int:budget_id>', methods=['DELETE'])
@jwt_required()
def delete_budget(budget_id: int):
    """Deletes a budget by its ID."""
    user_id = get_jwt_identity()
    budget_service.delete_budget(user_id=user_id, budget_id=budget_id)
    return '', 204