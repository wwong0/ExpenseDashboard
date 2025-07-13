import pytest
from app import create_app
from config import TestConfig
from models import db, User, Expense, Category, Tag
from validation_schemas.schemas import CreateExpenseSchema
from services import expense_service




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
    test_db.session.add(user1)
    test_db.session.commit()

    user1_cat1 = Category(name='Groceries', user_id=user1.id)
    user1_cat2 = Category(name='Utilities', user_id=user1.id)
    user1_tag1 = Tag(name='urgent', user_id=user1.id)
    user1_tag2 = Tag(name='recurring', user_id=user1.id)
    test_db.session.add_all([user1_cat1, user1_cat2, user1_tag1, user1_tag2])
    test_db.session.commit()

    user1_expense1_data = CreateExpenseSchema(
        name='Electricity Bill',
        amount=75.50,
        description='Monthly electricity',
        category_id=user1_cat1.id,
        tag_ids={user1_tag1.id}
    )
    user1_expense1 = expense_service.create_expense(user_id=user1.id, data=user1_expense1_data)

    user2 = User(username='user2', password_hash='password_hash_2')
    test_db.session.add(user2)
    test_db.session.commit()

    user2_cat1 = Category(name='Fast Food', user_id=user2.id)
    user2_cat2 = Category(name='Hobbies', user_id=user2.id)
    user2_tag1 = Tag(name='Red', user_id=user2.id)
    user2_tag2 = Tag(name='Blue', user_id=user2.id)
    test_db.session.add_all([user2_cat1, user2_cat2, user2_tag1, user2_tag2])
    test_db.session.commit()

    yield {
        "db": test_db,
        "user1": user1,
        "user2": user2,
        "user1_cat1": user1_cat1,
        "user1_cat2": user1_cat2,
        "user1_tag1": user1_tag1,
        "user1_tag2": user1_tag2,
        "user1_expense1": user1_expense1,
        "user2_cat1": user2_cat1,
        "user2_cat2": user2_cat2,
        "user2_tag1": user2_tag1,
        "user2_tag2": user2_tag2,
    }