from validation_schemas.schemas import AuthSchema
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

class UserAlreadyExistsError(Exception):
    pass

class InvalidCredentialError(Exception):
    pass

def register_user(data : AuthSchema):
    if User.query.filter_by(username=data.username).first():
        raise UserAlreadyExistsError(f'Username is taken')

    hashed_password = generate_password_hash(data.password)
    new_user = User(username=data.username, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return new_user

def login_user(data : AuthSchema):
    user = User.query.filter_by(username=data.username).first()
    if not user or not check_password_hash(user.password_hash, data.password):
        raise InvalidCredentialError(f'Invalid username or password')
    return user