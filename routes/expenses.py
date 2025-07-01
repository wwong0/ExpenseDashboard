from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_pydantic import validate

from validation_schemas.schemas import CreateExpenseSchema, UpdateExpenseSchema, ExpenseResponseSchema, \
    CategoryResponseSchema, TagResponseSchema
from services import expense_service

expense_bp = Blueprint('expenses', __name__)


@expense_bp.route('/expenses', methods=['GET'])
@jwt_required()
def get_all_expenses():
    """Retrieves all expenses for the authenticated user.

    Returns:
        A JSON list of the user's expenses and a 200 OK status.
    """
    user_id = get_jwt_identity()
    expenses = expense_service.get_all_expenses(user_id)
    response_data = [ExpenseResponseSchema.model_validate(e).model_dump() for e in expenses]
    return jsonify(response_data), 200


@expense_bp.route('/expenses/<int:expense_id>', methods=['GET'])
@jwt_required()
def get_expense(expense_id: int):
    """Retrieves a single expense by its ID.

    The expense must belong to the authenticated user.

    Args:
        expense_id: The unique identifier for the expense.

    Returns:
        A JSON object of the expense and a 200 OK status,
        or a 404 Not Found if the expense does not exist.
    """
    user_id = get_jwt_identity()
    expense = expense_service.get_expense_by_id(user_id, expense_id)
    response_data = ExpenseResponseSchema.model_validate(expense)
    return response_data.model_dump(), 200


@expense_bp.route('/expense_categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Retrieves all expense categories for the authenticated user.

    Returns:
        A JSON list of the user's categories and a 200 OK status.
    """
    user_id = get_jwt_identity()
    categories = expense_service.get_all_categories(user_id)
    response_data = [CategoryResponseSchema.model_validate(c).model_dump() for c in categories]
    return jsonify(response_data), 200


@expense_bp.route('/expense_tags', methods=['GET'])
@jwt_required()
def get_tags():
    """Retrieves all expense tags for the authenticated user.

    Returns:
        A JSON list of the user's tags and a 200 OK status.
    """
    user_id = get_jwt_identity()
    tags = expense_service.get_all_tags(user_id)
    response_data = [TagResponseSchema.model_validate(t).model_dump() for t in tags]
    return jsonify(response_data), 200


@expense_bp.route('/expenses', methods=['POST'])
@jwt_required()
@validate()
def create_expense(body: CreateExpenseSchema):
    """Creates a new expense for the authenticated user.

    Args:
        body: The expense data from the request body, validated by Pydantic.

    Returns:
        A JSON object of the newly created expense and a 201 Created status.
    """
    user_id = get_jwt_identity()
    new_expense = expense_service.create_expense(user_id=user_id, data=body)
    response_data = ExpenseResponseSchema.model_validate(new_expense)
    return response_data.model_dump(), 201


@expense_bp.route('/expenses/<int:expense_id>', methods=['PUT'])
@jwt_required()
@validate()
def update_expense(expense_id: int, body: UpdateExpenseSchema):
    """Updates an existing expense.

    The expense must belong to the authenticated user.

    Args:
        expense_id: The unique identifier for the expense to update.
        body: The updated expense data from the request body, validated by
            Pydantic.

    Returns:
        A JSON object of the updated expense and a 200 OK status.
    """
    user_id = get_jwt_identity()
    expense = expense_service.update_expense(user_id=user_id, expense_id=expense_id, data=body)
    response_data = ExpenseResponseSchema.model_validate(expense)
    return response_data.model_dump(), 200


@expense_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id: int):
    """Deletes an expense by its ID.

    The expense must belong to the authenticated user.

    Args:
        expense_id: The unique identifier for the expense to delete.

    Returns:
        An empty response with a 204 No Content status on success.
    """
    user_id = get_jwt_identity()
    expense_service.delete_expense(user_id=user_id, expense_id=expense_id)
    return '', 204