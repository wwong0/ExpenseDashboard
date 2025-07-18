from unittest.mock import patch, MagicMock


@patch('services.auth_service.register_user')
@patch('routes.auth.create_access_token', return_value = 'mocked_access_token')
def test_register(create_access_token, mocked_register_user, client):

    #GIVEN
    mock_user = MagicMock()
    mock_user.id = 1
    mocked_register_user.return_value = mock_user

    #WHEN
    response = client.post(
        '/auth/register',
        json = {'username': 'testuser', 'password': 'password'}
    )

    #THEN
    assert response.status_code == 201
    assert response.get_json() == {'access_token': 'mocked_access_token'}

@patch('services.auth_service.login_user')
@patch('routes.auth.create_access_token', return_value = 'mocked_access_token')
def test_login(create_access_token, mocked_login_user, client):

    #GIVEN
    mock_user = MagicMock()
    mock_user.id = 1
    mocked_login_user.return_value = mock_user

    #WHEN
    response = client.post(
        '/auth/login',
        json = {'username': 'testuser', 'password': 'password'}
    )

    #THEN
    assert response.status_code == 200
    assert response.get_json() == {'access_token': 'mocked_access_token'}
