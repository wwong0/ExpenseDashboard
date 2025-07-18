import pytest
from unittest.mock import patch

from services.auth_service import register_user, login_user, UserAlreadyExistsError, InvalidCredentialError
from models import User
from validation_schemas.schemas import AuthSchema

@patch('services.auth_service.generate_password_hash')
def test_register_user_success(mocked_generate_password_hash, test_db):
    """
    GIVEN valid authentication data for a new user
    WHEN the register_user service is called
    THEN a new User object should be created in the database with a hashed password
    """
    #GIVEN
    auth_data = AuthSchema(username= 'testuser', password='testpassword')
    mocked_generate_password_hash.return_value = 'hashed_password'

    #WHEN
    new_user = register_user(auth_data)

    #THEN
    assert new_user.username == 'testuser'
    assert new_user.password_hash == 'hashed_password'
    retrieved_user = User.query.filter_by(username='testuser').first()
    assert retrieved_user == new_user

def test_register_user_user_already_exists(seeded_test_db):
    """
    GIVEN an existing user in the database
    WHEN an attempt is made to register a new user with the same username
    THEN a UserAlreadyExistsError should be raised
    """
    #GIVEN
    auth_data = AuthSchema(username=seeded_test_db['user1'].username, password='testpassword')

    #WHEN/THEN
    with pytest.raises(UserAlreadyExistsError):
        register_user(auth_data)

@patch('services.auth_service.check_password_hash', return_value=True)
def test_login_user_success(mock_check_password_hash, seeded_test_db):

    #GIVEN
    auth_data = AuthSchema(username=seeded_test_db['user1'].username, password='password')

    #WHEN
    authenticated_user = login_user(auth_data)

    #THEN
    assert authenticated_user == seeded_test_db['user1']

@patch('services.auth_service.check_password_hash', return_value = False)
def test_login_user_invalid_credentials(mock_check_password_hash, seeded_test_db):

    #GIVEN
    auth_data = AuthSchema(username=seeded_test_db['user1'].username, password='invalid_password')

    #WHEN/THEN
    with pytest.raises(InvalidCredentialError):
        login_user(auth_data)


