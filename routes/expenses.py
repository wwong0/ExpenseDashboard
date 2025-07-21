from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_pydantic import validate


from validation_schemas.schemas import CreateExpenseSchema, UpdateExpenseSchema, ExpenseResponseSchema, \
    CategoryResponseSchema, TagResponseSchema, TagLookupSchema
from services import expense_service
from utils.route_utils import pagination_to_response_data

expense_bp = Blueprint('expenses', __name__)

@expense_bp.route('/expenses', methods=['GET'])
@jwt_required()
def get_all_expenses():
    """Retrieves all expenses for the authenticated user.

    Returns:
        A JSON object of the user's expenses and pagination metadata.
    """
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = expense_service.get_all_expenses(user_id, page=page, per_page=per_page)

    response_data = pagination_to_response_data(pagination, ExpenseResponseSchema)

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

@expense_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_all_categories():
    """Retrieves all expense categories for the authenticated user.

    Returns:
        A JSON object of the user's categories and pagination metadata.
    """
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = expense_service.get_all_categories(user_id, page=page, per_page=per_page)

    response_data = pagination_to_response_data(pagination, CategoryResponseSchema)

    return jsonify(response_data), 200

@expense_bp.route('/categories/<int:category_id>', methods=['GET'])
@jwt_required()
def get_category(category_id: int):
    """Retrieves a single category by its ID.

    The category must belong to the authenticated user.

    Args:
        category_id: The unique identifier for the expense.

    Returns:
        A JSON object of the category and a 200 OK status,
        or a 404 Not Found if the category does not exist.
    """
    user_id = get_jwt_identity()
    category = expense_service.get_category_by_id(user_id, category_id)
    response_data = CategoryResponseSchema.model_validate(category)
    return response_data.model_dump(), 200


@expense_bp.route('/tags', methods=['GET'])
@jwt_required()
def get_all_tags():
    """
    Retrieves a paginated list of all expense tags for the authenticated user.

    This endpoint supports pagination via 'page' and 'per_page' query params.
    Example: GET /api/tags?page=1&per_page=10

    Returns:
        A JSON object containing the list of tags and pagination metadata.
    """
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = expense_service.get_all_tags(user_id=user_id, page=page, per_page=per_page)

    response_data = pagination_to_response_data(pagination, TagResponseSchema)
    return jsonify(response_data), 200


@expense_bp.route('/tags/lookup', methods=['POST'])
@jwt_required()
@validate()
def lookup_tags(body: TagLookupSchema):
    """
    Retrieves a specific set of tags by their IDs.

    This is useful for fetching multiple known resources in a single request.
    The response is an unpaginated list of the found tags.

    Args:
        body: A JSON object with a "tag_ids" key containing a list of integers.
              Example: { "tag_ids": [1, 5, 12] }

    Returns:
        A JSON array of the requested tag objects.
    """
    user_id = get_jwt_identity()

    tags = expense_service.get_tags_by_ids(user_id=user_id, tag_ids=body.tag_ids)

    response_data = [TagResponseSchema.model_validate(t).model_dump() for t in tags]
    return jsonify(response_data), 200


@expense_bp.route('/tags/<int:tag_id>', methods=['GET'])
@jwt_required()
def get_tag(tag_id: int):
    """Retrieves a single tag by its ID.

    The tag must belong to the authenticated user.

    Args:
        tag_id: The unique identifier for the expense.

    Returns:
        A JSON object of the tag and a 200 OK status,
        or a 404 Not Found if the tag does not exist.
    """
    user_id = get_jwt_identity()
    tag = expense_service.get_tag_by_id(user_id, tag_id)
    response_data = TagResponseSchema.model_validate(tag)
    return response_data.model_dump(), 200


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