import json
from unittest.mock import patch
from decimal import Decimal

from services import NotFoundError
from services.budget_service import BudgetAlreadyExistsError
from tests.testing_utils import create_auth_headers_for_id
from validation_schemas.schemas import BudgetResponseSchema

def budget_to_json_loaded_validated_response(budget):
    """Serializes a budget model object to a JSON-loaded dict via its Pydantic schema."""
    return json.loads(BudgetResponseSchema.model_validate(budget).model_dump_json())

def assert_budget_dicts_equal(actual: dict, expected: dict):
    """
    Asserts that two budget dictionaries are equal, handling the
    Decimal-to-float conversion for the 'amount' field.
    """
    actual_copy = actual.copy()
    expected_copy = expected.copy()

    if 'amount' in actual_copy and 'amount' in expected_copy:
        actual_copy['amount'] = float(actual_copy['amount'])
        expected_copy['amount'] = float(expected_copy['amount'])

    assert actual_copy == expected_copy

@patch('routes.budgets.budget_service.create_budget')
def test_create_budget_success(mock_create_budget, client, auth_headers_user1, mocked_budget_object):
    """
    GIVEN a request to create a budget
    WHEN the service layer successfully creates the budget
    THEN the route should return a 201 status and the serialized budget data.
    """
    # GIVEN
    request_data = {'amount': 500.00, 'year': 2025, 'month': 7, 'category_id': 1}
    mock_create_budget.return_value = mocked_budget_object
    expected_response = budget_to_json_loaded_validated_response(mocked_budget_object)

    # WHEN
    response = client.post('/api/budgets', headers=auth_headers_user1, json=request_data)

    # THEN
    assert response.status_code == 201
    assert_budget_dicts_equal(response.get_json(), expected_response)
    mock_create_budget.assert_called_once()

@patch('routes.budgets.budget_service.create_budget')
def test_create_budget_conflict(mock_create_budget, client, auth_headers_user1):
    """
    GIVEN a request to create a budget that already exists
    WHEN the service layer raises BudgetAlreadyExistsError
    THEN the route should return a 409 Conflict status.
    """
    # GIVEN
    request_data = {'amount': 500.00, 'year': 2025, 'month': 7, 'category_id': 1}
    mock_create_budget.side_effect = BudgetAlreadyExistsError("Budget already exists.")

    # WHEN
    response = client.post('/api/budgets', headers=auth_headers_user1, json=request_data)

    # THEN
    assert response.status_code == 409
    assert response.get_json()['error'] == "Budget already exists."

@patch('routes.budgets.budget_service.get_budget_by_year_month')
def get_budget_summary_for_month(mock_get_budgets, client, auth_headers_user1, mocked_budget_object):
    """
    GIVEN a request to get budgets for a specific month
    WHEN the service layer returns budget data
    THEN the route should return a 200 OK status with the serialized data.
    """
    # GIVEN
    # The service returns model objects, which the route then serializes.
    service_return_value = {
        'overall': None,
        'categorical': [mocked_budget_object]
    }
    mock_get_budgets.return_value = service_return_value

    # WHEN
    response = client.get('/api/budgets/summary?year=2025&month=7', headers=auth_headers_user1)

    # THEN
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data == service_return_value

@patch('routes.budgets.budget_service.update_budget')
def test_update_budget_success(mock_update_budget, client, auth_headers_user1, mocked_budget_object):
    """
    GIVEN a request to update a budget
    WHEN the service layer successfully updates the budget
    THEN the route should return a 200 OK status and the updated data.
    """
    # GIVEN
    budget_id = mocked_budget_object.id
    request_data = {'amount': 550.50}
    # Mock the return value to reflect the update
    mocked_budget_object.amount = Decimal('550.50')
    mock_update_budget.return_value = mocked_budget_object
    expected_response = budget_to_json_loaded_validated_response(mocked_budget_object)

    # WHEN
    response = client.put(f'/api/budgets/{budget_id}', headers=auth_headers_user1, json=request_data)

    # THEN
    assert response.status_code == 200
    assert_budget_dicts_equal(response.get_json(), expected_response)
    mock_update_budget.assert_called_once()

@patch('routes.budgets.budget_service.delete_budget')
@patch('routes.budgets.get_jwt_identity', return_value = 123)
def test_delete_budget_success(mock_get_jwt_identity, mock_delete_budget, client):
    """
    GIVEN a request to delete a budget
    WHEN the service layer successfully deletes it
    THEN the route should return a 204 No Content status.
    """
    # GIVEN
    budget_id = 1
    mock_delete_budget.return_value = True

    # WHEN
    response = client.delete(f'/api/budgets/{budget_id}', headers=create_auth_headers_for_id(123))

    # THEN
    assert response.status_code == 204
    mock_delete_budget.assert_called_once_with(user_id=123, budget_id=budget_id)

@patch('routes.budgets.budget_service.delete_budget')
def test_delete_budget_not_found(mock_delete_budget, client, auth_headers_user1):
    """
    GIVEN a request to delete a budget that does not exist
    WHEN the service layer raises NotFoundError
    THEN the route should return a 404 Not Found status.
    """
    # GIVEN
    budget_id = 999
    mock_delete_budget.side_effect = NotFoundError("Budget not found.")

    # WHEN
    response = client.delete(f'/api/budgets/{budget_id}', headers=auth_headers_user1)

    # THEN
    assert response.status_code == 404
    assert response.get_json()['error'] == "Budget not found."