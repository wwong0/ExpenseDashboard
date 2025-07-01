import pytest
from app import create_app
from config import TestConfig
from models import db


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