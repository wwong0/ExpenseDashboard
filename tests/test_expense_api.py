from unittest.mock import patch
from flask_jwt_extended import create_access_token
import datetime


from routes.expenses import pagination_to_response_data
from models import Category, Expense
from validation_schemas.schemas import CategoryResponseSchema, ExpenseResponseSchema, TagResponseSchema


def create_auth_headers_for_id(identity: int | str) -> dict:
    """
    Creates a JWT authorization header for a given identity.
    """
    access_token = create_access_token(identity=str(identity))
    return {'Authorization': f'Bearer {access_token}'}

def convert_json_date_to_datetime(date_str : str) -> datetime.date:
    return datetime.datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z').date()

def assert_expense_dicts_equal(actual: dict, expected: dict):
    """Helper to compare two expense dictionaries, handling date conversion."""
    actual['date'] = convert_json_date_to_datetime(actual['date'])
    assert actual == expected

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

    # WHEN
    response = client.get('/api/expenses', headers=auth_headers_user1)

    # THEN
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['total'] == 2

    retrieved_expenses = {item['id']: item for item in json_data['items']}
    assert len(retrieved_expenses) == 2

    assert_expense_dicts_equal(retrieved_expenses[user1_expense1.id], expected_expenses[user1_expense1.id])
    assert_expense_dicts_equal(retrieved_expenses[user1_expense2.id], expected_expenses[user1_expense2.id])

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

    assert_expense_dicts_equal(json_data, expected_expense)

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
    """
    GIVEN a logged-in user with an existing category with id <category_id>
    WHEN a GET request is made to /api/categories/<category_id>
    THEN it should return a 200 OK status with the user's category with id <category_id>
    """
    #GIVEN
    cat1 = seeded_test_db['user1_cat1']
    expected_category = CategoryResponseSchema.model_validate(cat1).model_dump()

    #WHEN
    response = client.get(f'/api/categories/{cat1.id}', headers=auth_headers_user1)

    #THEN
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data == expected_category

def test_get_all_tags(client, auth_headers_user1, seeded_test_db):
    """
    GIVEN a logged-in user with existing tags
    WHEN a GET request is made to /api/tags
    THEN it should return a 200 OK status with the user's paginated tags
    """
    #GIVEN
    tag1 = seeded_test_db['user1_tag1']
    tag2 = seeded_test_db['user1_tag2']
    tag3 = seeded_test_db['user1_tag3']
    expected_tags = {tag1.id: TagResponseSchema.model_validate(tag1).model_dump(),
                     tag2.id: TagResponseSchema.model_validate(tag2).model_dump(),
                     tag3.id: TagResponseSchema.model_validate(tag3).model_dump()}

    #WHEN
    response = client.get('/api/tags', headers=auth_headers_user1)

    #THEN
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['total'] == 3
    actual_tags = {item['id']: item for item in json_data['items']}
    assert actual_tags == expected_tags

def test_get_tag(client, auth_headers_user1, seeded_test_db):
    """
    GIVEN a logged-in user with an existing tag with id <tag_id>
    WHEN a GET request is made to /api/tags/<tag_id>
    THEN it should return a 200 OK status with the user's tag with id <tag_id>
    """
    #GIVEN
    tag1 = seeded_test_db['user1_tag1']
    expected_tag = TagResponseSchema.model_validate(tag1).model_dump()

    #WHEN
    response = client.get(f'/api/tags/{tag1.id}', headers=auth_headers_user1)

    #THEN
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data == expected_tag

def test_lookup_tags_success(client, auth_headers_user1, seeded_test_db):
    """
    GIVEN a logged-in user and a list of valid tag IDs
    WHEN a POST request is made to /api/tags/lookup with a list of tag_ids
    THEN it should return a 200 OK status with the requested tags
    """
    #GIVEN
    tag1 = seeded_test_db['user1_tag1']
    tag3 = seeded_test_db['user1_tag3']
    expected_tags = sorted([tag1,tag3], key = lambda x: x.id)
    expected_tags = [TagResponseSchema.model_validate(t).model_dump() for t in expected_tags]

    #WHEN
    response = client.post('/api/tags/lookup', headers=auth_headers_user1, json ={
        "tag_ids": [tag1.id, tag3.id]
    })

    #THEN
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data == expected_tags

@patch('routes.expenses.expense_service.create_expense')
@patch('routes.expenses.get_jwt_identity', return_value = 123)
def test_create_expense_success(mock_get_jwt_identity, mock_create_expense, client, mocked_db_objects):
    """
   GIVEN a request to create an expense
   WHEN the service layer successfully creates the expense
   THEN the route should return a 201 status and the serialized expense data.
   """
    #GIVEN
    request_data = {
        'name' : 'test expense',
        'amount' : 0,
    }

    mock_create_expense.return_value = mocked_db_objects['mocked_expense']
    expected_response_data = ExpenseResponseSchema.model_validate(mocked_db_objects['mocked_expense']).model_dump()

    #WHEN
    response = client.post(
        '/api/expenses',
        headers=create_auth_headers_for_id(123),
        json=request_data
    )

    #THEN
    assert response.status_code == 201
    json_data = response.get_json()
    assert_expense_dicts_equal(json_data, expected_response_data)

@patch('routes.expenses.expense_service.update_expense')
@patch('routes.expenses.get_jwt_identity', return_value = 123)
def test_update_expense(mock_get_jwt_identity, mock_update_expense, client, mocked_db_objects):

    #GIVEN
    request_data = {}
    mock_update_expense.return_value = mocked_db_objects['mocked_expense']
    expected_response_data = ExpenseResponseSchema.model_validate(mocked_db_objects['mocked_expense']).model_dump()

    # WHEN
    response = client.put(
        f'/api/expenses/{mocked_db_objects["mocked_expense"].id}',
        headers=create_auth_headers_for_id(123),
        json=request_data
    )

    # THEN
    assert response.status_code == 200
    json_data = response.get_json()
    assert_expense_dicts_equal(json_data, expected_response_data)


@patch('routes.expenses.expense_service.delete_expense')
@patch('routes.expenses.get_jwt_identity', return_value = 123)
def test_delete_expense(mock_get_jwt_identity, mock_delete_expense, client, mocked_db_objects):

    #GIVEN
    expense_id = mocked_db_objects['mocked_expense'].id
    mock_delete_expense.return_value = True

    #WHEN
    response = client.delete(
        f'/api/expenses/{expense_id}',
        headers=create_auth_headers_for_id(123),
    )

    # THEN
    assert response.status_code == 204

