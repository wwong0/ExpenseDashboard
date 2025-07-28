import json

from flask_jwt_extended import create_access_token



def create_auth_headers_for_id(identity: int | str) -> dict:
    """
    Creates a JWT authorization header for a given identity.
    """
    access_token = create_access_token(identity=str(identity))
    return {'Authorization': f'Bearer {access_token}'}

