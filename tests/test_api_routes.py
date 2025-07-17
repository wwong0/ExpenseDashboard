import pytest
from flask import jsonify
from flask_jwt_extended import create_access_token
from datetime import datetime

from routes.expenses import pagination_to_response_data
from models import Category, Expense
from validation_schemas.schemas import CategoryResponseSchema, ExpenseResponseSchema

def convert_json_date_to_datetime(date_str : str) -> datetime.date:
    return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z').date()

def test_pagination_to_response_data(seeded_test_db):
    """
    GIVEN a Pagination object with items and metadata
    WHEN pagination_to_response_data is called
    THEN it should return a dictionary with serialized items and correct pagination metadata.
    """
    # GIVEN
    cat1 = seeded_test_db['user1_cat1']
    cat2 = seeded_test_db['user1_cat2']

    query = Category.query.filter_by(user_id=seeded_test_db['user1'].id)
    query = query.order_by(Category.name)
    pag = query.paginate(page=1, per_page=20, error_out=False)

    #WHEN
    response_data = pagination_to_response_data(pag, CategoryResponseSchema)

    #THEN
    assert response_data['items'] == [CategoryResponseSchema.model_validate(cat1).model_dump(),
                                      CategoryResponseSchema.model_validate(cat2).model_dump()]
    assert response_data['total'] == 2
    assert response_data['pages'] == 1
    assert response_data['current_page'] == 1
    assert response_data['per_page'] == 20
    assert response_data['has_next'] is False
    assert response_data['has_prev'] is False

def test_pagination_to_response_data_no_items(seeded_test_db):
    """
    GIVEN an empty Pagination object
    WHEN pagination_to_response_data is called
    THEN it should return a dictionary with an empty items list and correct pagination metadata.
    """
    # GIVEN
    query = Expense.query.filter_by(user_id=seeded_test_db['user3'].id)
    pag = query.paginate(page=1, per_page=20, error_out=False)
    #WHEN
    response_data = pagination_to_response_data(pag, CategoryResponseSchema)
    #THEN
    assert response_data['items'] == []

def test_get_all_expenses_success(client, auth_headers_user1, seeded_test_db):
    """
    GIVEN a logged-in user with existing expenses
    WHEN a GET request is made to /api/expenses
    THEN it should return a 200 OK status with the user's paginated expenses
    """
    # GIVEN
    user1_expense1 = seeded_test_db['user1_expense1']
    user1_expense2 = seeded_test_db['user1_expense2']

    expected_expenses = {
        user1_expense1.id: ExpenseResponseSchema.model_validate(user1_expense1).model_dump(),
        user1_expense2.id: ExpenseResponseSchema.model_validate(user1_expense2).model_dump()
    }
    expected_dates = {expense_id: expected_expenses[expense_id].pop('date') for expense_id in expected_expenses}

    # WHEN
    response = client.get('/api/expenses', headers=auth_headers_user1)

    # THEN
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['total'] == 2

    retrieved_expenses = {item['id']: item for item in json_data['items']}
    assert len(retrieved_expenses) == 2

    actual_dates = {expense_id: convert_json_date_to_datetime(retrieved_expenses[expense_id].pop('date')) for expense_id in retrieved_expenses}
    assert retrieved_expenses[user1_expense1.id] == expected_expenses[user1_expense1.id]
    assert retrieved_expenses[user1_expense2.id] == expected_expenses[user1_expense2.id]
    assert expected_dates == actual_dates

def test_get_expense(client, auth_headers_user1, seeded_test_db):
    """
   GIVEN a logged-in user with an existing expense with id <expense_id>
   WHEN a GET request is made to /api/expenses/<expense_id>
   THEN it should return a 200 OK status with the user's expense with id <expense_id>
   """
    #GIVEN
    user1_expense1 = seeded_test_db['user1_expense1']
    expected_expense = ExpenseResponseSchema.model_validate(user1_expense1).model_dump()

    #WHEN
    response = client.get(f'/api/expenses/{user1_expense1.id}', headers= auth_headers_user1)

    #THEN
    assert response.status_code == 200
    json_data = response.get_json()

    actual_date_str = json_data.pop('date')
    expected_date_obj = expected_expense.pop('date')

    assert expected_expense == json_data
    actual_date_obj = convert_json_date_to_datetime(actual_date_str)
    assert actual_date_obj == expected_date_obj

def test_get_all_categories(client, auth_headers_user1, seeded_test_db):
    """
    GIVEN a logged-in user with existing categories
    WHEN a GET request is made to /api/categories
    THEN it should return a 200 OK status with the user's paginated categories
    """
    #GIVEN
    cat1 = seeded_test_db['user1_cat1']
    cat2 = seeded_test_db['user1_cat2']
    expected_categories = {cat1.id: CategoryResponseSchema.model_validate(cat1).model_dump(),
                           cat2.id: CategoryResponseSchema.model_validate(cat2).model_dump()}

    #WHEN
    response = client.get('/api/categories', headers=auth_headers_user1)

    #THEN
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['total'] == 2
    actual_categories = {item['id']: item for item in json_data['items']}
    assert actual_categories == expected_categories

def test_get_category(client, auth_headers_user1, seeded_test_db):

    #GIVEN
    cat1 = seeded_test_db['user1_cat1']
    expected_category = CategoryResponseSchema.model_validate(cat1).model_dump()

    #WHEN
    response = client.get(f'/api/categories/{cat1.id}', headers=auth_headers_user1)

    #THEN
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data == expected_category





