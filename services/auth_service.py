from werkzeug.security import generate_password_hash, check_password_hash

from validation_schemas.schemas import AuthSchema
from models import db, User


class UserAlreadyExistsError(Exception):
    """Custom exception raised when a user tries to register with a username that already exists."""
    pass


class InvalidCredentialError(Exception):
    """Custom exception raised for failed login attempts due to wrong username or password."""
    pass


def register_user(data: AuthSchema):
    """
    Handles the business logic for registering a new user.

    Args:
        data: An AuthSchema object containing the username and password.

    Raises:
        UserAlreadyExistsError: If the username is already taken.

    Returns:
        The newly created User object.
    """
    if User.query.filter_by(username=data.username).first():
        raise UserAlreadyExistsError(f'Username is taken')

    hashed_password = generate_password_hash(data.password)
    new_user = User(username=data.username, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return new_user


def login_user(data: AuthSchema):
    """
    Handles the business logic for logging in a user.

    Args:
        data: An AuthSchema object containing the username and password.

    Raises:
        InvalidCredentialError: If the username does not exist or the password is incorrect.

    Returns:
        The authenticated User object.
    """
    user = User.query.filter_by(username=data.username).first()
    if not user or not check_password_hash(user.password_hash, data.password):
        raise InvalidCredentialError(f'Invalid username or password')
    return user