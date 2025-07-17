import pytest
import datetime
from flask_jwt_extended import create_access_token

from app import create_app
from config import TestConfig
from models import db, User, Expense, Category, Tag
from validation_schemas.schemas import CreateExpenseSchema
from services.expense_service import create_expense

@pytest.fixture(scope='function')
def test_app():
    """
    Pytest fixture to create and configure a new app instance for testing.
    this fixture will be set up once per test function.
    """
    app = create_app(TestConfig)
    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def test_db(test_app):
    """
    Pytest fixture to set up and tear down the database for each test function.

    This fixture depends on the 'test_app' fixture, which provides the app
    context. It creates all database tables before a test runs and drops them
    all after the test completes, ensuring a clean state for every test.

    Args:
        test_app: The test Flask application instance from the 'test_app' fixture.

    Yields:
        The SQLAlchemy database instance.
    """
    with test_app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def seeded_test_db(test_db):
    """
    Pytest fixture that seeds the database with initial data for testing.

    This provides a consistent starting state for tests that require
    pre-existing data, such as users, categories, tags, and expenses.
    It returns a dictionary containing the created objects for easy access.
    """

    user1 = User(username='user1', password_hash='password_hash_1')
    user1_cat1 = Category(name='Groceries', user = user1)
    user1_cat2 = Category(name='Utilities', user = user1)
    user1_tag1 = Tag(name='urgent', user = user1)
    user1_tag2 = Tag(name='recurring', user = user1)
    user1_tag3 = Tag(name='weekly', user = user1)

    test_db.session.add_all([user1,
                             user1_cat1,
                             user1_cat2,
                             user1_tag1,
                             user1_tag2,
                             user1_tag3])
    test_db.session.commit()

    user1_expense1_data = CreateExpenseSchema(
        name='Milk and Eggs',
        amount=15.25,
        description='Weekly groceries',
        date=datetime.date(2025, 7, 7),
        active_status=True,
        category_id=user1_cat1.id,
        tag_ids={user1_tag1.id}
    )

    user1_expense1 = create_expense(user_id=user1.id, data=user1_expense1_data)

    user1_expense2_data = CreateExpenseSchema(
        name='Electricity Bill',
        amount=75.50,
        description='Monthly electricity',
        date = datetime.date(2025, 7, 7),
        active_status = True,
        category_id=user1_cat2.id,
        tag_ids={user1_tag1.id, user1_tag2.id}
    )

    user1_expense2 = create_expense(user_id=user1.id, data=user1_expense2_data)


    user2 = User(username='user2', password_hash='password_hash_2')
    user2_cat1 = Category(name='Fast Food', user = user2)
    user2_cat2 = Category(name='Hobbies', user = user2)
    user2_tag1 = Tag(name='Red', user = user2)
    user2_tag2 = Tag(name='Blue', user = user2)

    test_db.session.add_all([user2,
                             user2_cat1,
                             user2_cat2,
                             user2_tag1,
                             user2_tag2])
    test_db.session.commit()

    user2_expense1_data = CreateExpenseSchema(
        name='Burger King',
        amount=10.00,
        description='Lunch',
        date = datetime.date(2025, 7, 7),
        active_status = True,
        category_id=user2_cat1.id,
        tag_ids={user2_tag1.id}
    )
    user2_expense1 = create_expense(user_id=user2.id, data=user2_expense1_data)

    user3 = User(username='user3', password_hash='password_hash_3')
    test_db.session.add_all([user3,])
    test_db.session.commit()



    yield {
        "db": test_db,
        "user1": user1,
        "user2": user2,
        "user1_cat1": user1_cat1,
        "user1_cat2": user1_cat2,
        "user1_tag1": user1_tag1,
        "user1_tag2": user1_tag2,
        "user1_tag3": user1_tag3,
        "user1_expense1": user1_expense1,
        "user1_expense2": user1_expense2,
        "user2_cat1": user2_cat1,
        "user2_cat2": user2_cat2,
        "user2_tag1": user2_tag1,
        "user2_tag2": user2_tag2,
        "user2_expense1": user2_expense1,
        'user3' : user3
    }

@pytest.fixture(scope='function')
def auth_headers_user1(seeded_test_db):
    """
    Pytest fixture that returns JWT authentication headers for user1.
    Depends on the seeded_test_db to ensure the user exists.
    """
    user1_id = seeded_test_db['user1'].id
    access_token = create_access_token(identity=str(user1_id))
    return {
        'Authorization': f'Bearer {access_token}'
    }

@pytest.fixture(scope='function')
def auth_headers_user2(seeded_test_db):
    """
    Pytest fixture that returns JWT authentication headers for user2.
    """
    user2_id = seeded_test_db['user2'].id
    access_token = create_access_token(identity=str(user2_id))
    return {
        'Authorization': f'Bearer {access_token}'
    }

@pytest.fixture(scope='function')
def auth_headers_user3(seeded_test_db):
    """
    Pytest fixture that returns JWT authentication headers for user3.
    """
    user3_id = seeded_test_db['user3'].id
    access_token = create_access_token(identity=str(user3_id))
    return {
        'Authorization': f'Bearer {access_token}'
    }

@pytest.fixture(scope='function')
def client(test_app):
    """
    Pytest fixture to provide a Flask test client for making requests.
    This allows tests to simulate HTTP requests to the application.
    """
    return test_app.test_client()


@pytest.fixture(scope='function')
def auth_headers(client):
    """
    Pytest fixture to handle user login and provide JWT auth headers.
    This simplifies testing protected endpoints by abstracting away the
    login process. It returns a dictionary containing headers for two users.
    """
    # Helper function to log in a user and get their token
    def get_token(username, password):
        response = client.post('/auth/login', json={
            'username': username,
            'password': 'password' # Assuming a known password for test users
        })
        assert response.status_code == 200
        return response.get_json()['access_token']