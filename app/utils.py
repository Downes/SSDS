# utils.py
from functools import wraps
from flask import request, jsonify
from flask_login import current_user
import jwt
from datetime import datetime, timedelta
from config import Config

def login_required_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'You must be logged in to access this resource'}), 401
        return f(*args, **kwargs)
    return decorated_function

def generate_token(user_id):
    expiration = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
    token = jwt.encode({
        'user_id': user_id,
        'exp': expiration
    }, Config.SECRET_KEY, algorithm='HS256')
    return token
