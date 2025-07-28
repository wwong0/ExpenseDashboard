from unittest.mock import patch
import json

from tests.testing_utils import create_auth_headers_for_id
from validation_schemas.schemas import IncomeResponseSchema

def income_to_json_loaded_validated_response(income):
    return json.loads(IncomeResponseSchema.model_validate(income).model_dump_json())

def assert_income_dicts_equal(actual: dict, expected: dict):
    """
    Asserts that two income dictionaries are equal, handling the
    Decimal-to-float conversion for the 'amount' field.
    """
    actual_copy = actual.copy()
    expected_copy = expected.copy()

    if 'amount' in actual_copy and 'amount' in expected_copy:
        # Convert both to float for a consistent comparison
        actual_copy['amount'] = float(actual_copy['amount'])
        expected_copy['amount'] = float(expected_copy['amount'])

    assert actual_copy == expected_copy

def test_get_all_incomes_success(client, auth_headers_user1, seeded_test_db):
    """
    GIVEN a logged-in user with an existing income
    WHEN a GET request is made to /incomes
    THEN it should return a 200 OK status with the user's paginated incomes
    """
    # GIVEN
    user1_income1 = seeded_test_db['user1_income1']
    expected_income = income_to_json_loaded_validated_response(user1_income1)

    # WHEN
    response = client.get('/api/incomes', headers=auth_headers_user1)

    # THEN
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['total'] == 1
    assert len(json_data['items']) == 1
    assert_income_dicts_equal(json_data['items'][0], expected_income)

def test_get_income_success(client, auth_headers_user1, seeded_test_db):
    """
    GIVEN a logged-in user with an existing income
    WHEN a GET request is made to /incomes/<income_id>
    THEN it should return a 200 OK status with the correct income
    """
    # GIVEN
    user1_income1 = seeded_test_db['user1_income1']
    expected_income = income_to_json_loaded_validated_response(user1_income1)

    # WHEN
    response = client.get(f'/api/incomes/{user1_income1.id}', headers=auth_headers_user1)

    # THEN
    assert response.status_code == 200
    assert_income_dicts_equal(response.get_json(), expected_income)

@patch('routes.incomes.income_service.create_income')
def test_create_income_success(mock_create_income, client, auth_headers_user1, mocked_income_object):
    """
    GIVEN a request to create an income
    WHEN the service layer successfully creates the income
    THEN the route should return a 201 status and the serialized income data.
    """
    # GIVEN
    request_data = {'source': 'Test Income', 'amount': 100.00}
    mock_create_income.return_value = mocked_income_object
    expected_response = income_to_json_loaded_validated_response(mocked_income_object)

    # WHEN
    response = client.post('/api/incomes', headers=auth_headers_user1, json=request_data)

    # THEN
    assert response.status_code == 201
    assert_income_dicts_equal(response.get_json(), expected_response)

@patch('routes.incomes.income_service.update_income')
def test_update_income_success(mock_update_income, client, auth_headers_user1, mocked_income_object):
    """
    GIVEN a request to update an income
    WHEN the service layer successfully updates the income
    THEN the route should return a 200 status and the serialized income data.
    """
    # GIVEN
    income_id = mocked_income_object.id
    request_data = {'amount': 1500.00}
    mock_update_income.return_value = mocked_income_object
    expected_response = income_to_json_loaded_validated_response(mocked_income_object)

    # WHEN
    response = client.put(f'/api/incomes/{income_id}', headers=auth_headers_user1, json=request_data)

    # THEN
    assert response.status_code == 200
    assert_income_dicts_equal(response.get_json(), expected_response)
    mock_update_income.assert_called_once()

@patch('routes.incomes.income_service.delete_income')
@patch('routes.incomes.get_jwt_identity', return_value = 123)
def test_delete_income_success(mock_get_jwt_identity, mock_delete_income, client):
    """
    GIVEN a request to delete an income
    WHEN the service layer successfully deletes the income
    THEN the route should return a 204 No Content status.
    """
    # GIVEN
    income_id = 1
    mock_delete_income.return_value = True

    # WHEN
    response = client.delete(f'/api/incomes/{income_id}', headers=create_auth_headers_for_id(123))

    # THEN
    assert response.status_code == 204
    mock_delete_income.assert_called_once_with(user_id=123, income_id=income_id)