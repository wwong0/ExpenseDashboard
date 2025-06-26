from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_pydantic import validate

from validation_schemas.schemas import CreateExpenseSchema, UpdateExpenseSchema, ExpenseResponseSchema, \
    CategoryResponseSchema, TagResponseSchema
from services import expense_service

expense_bp = Blueprint('expenses', __name__)

@expense_bp.route('/expenses', methods=['GET'])
@jwt_required()
def get_all_expenses():
    user_id = get_jwt_identity()
    expenses = expense_service.get_all_expenses(user_id)
    response_data = [ExpenseResponseSchema.model_validate(expense) for expense in expenses]
    return [exp.model_dump() for exp in response_data], 200

@expense_bp.route('/expenses/<int:expense_id>', methods=['GET'])
@jwt_required()
def get_expense(expense_id):
    user_id = get_jwt_identity()

    expense = expense_service.get_expense_by_id(user_id, expense_id)
    response_data = ExpenseResponseSchema.model_validate(expense)
    return response_data.model_dump_json(), 200

@expense_bp.route('/expense_categories', methods=['GET'])
@jwt_required()
def get_categories():
    user_id = get_jwt_identity()
    categories = expense_service.get_all_categories(user_id)
    response_data = [CategoryResponseSchema.model_validate(cat) for cat in categories]
    return [cat.model_dump() for cat in response_data], 200

@expense_bp.route('/expense_tags', methods=['GET'])
@jwt_required()
def get_tags():
    user_id = get_jwt_identity()

    tags = expense_service.get_all_tags(user_id)
    response_data = [TagResponseSchema.model_validate(tag) for tag in tags]
    return [tag.model_dump() for tag in response_data], 200

@expense_bp.route('/expenses', methods=['POST'])
@jwt_required()
@validate(CreateExpenseSchema)
def create_expense(body : CreateExpenseSchema):

    user_id = get_jwt_identity()
    new_expense = expense_service.create_expense(user_id= user_id, data = body)
    response_data = ExpenseResponseSchema.model_validate(new_expense)
    return response_data.model_dump_json(), 201


@expense_bp.route('/expenses/<int:expense_id>', methods=['PUT'])
@jwt_required()
@validate(UpdateExpenseSchema)
def update_expense(expense_id : int, body : UpdateExpenseSchema):
    user_id = get_jwt_identity()

    expense = expense_service.update_expense(user_id = user_id, expense_id= expense_id, data = body)
    response_data = ExpenseResponseSchema.model_validate(expense)
    return response_data.model_dump_json(), 200

@expense_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id : int):
    user_id = get_jwt_identity()

    expense_service.delete_expense(user_id = user_id, expense_id = expense_id)
    return '', 204


