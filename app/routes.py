from flask import Blueprint, request, jsonify
from markupsafe import escape
from models import KeyValue
from app import db  # Import the db instance from app.py
from utils import login_required_json  # Import the decorator from utils.py
from functools import wraps
import jwt
from config import Config  
from models import *


routes_bp = Blueprint('routes', __name__)

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header must start with "Bearer "'}), 401
        token = auth_header.split(' ')[1]  # Extract the token after "Bearer "

        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            authenticated_user = User.query.get(data['user_id'])
            if not authenticated_user:
                return jsonify({'error': 'User not found!'}), 404
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401
        return f(authenticated_user, *args, **kwargs)  # Pass authenticated_user
    return decorated_function

@auth_bp.route("/refresh_token", methods=['POST'])
def refresh_token():
    refresh_token = request.headers.get('Authorization').split(' ')[1]
    try:
        data = jwt.decode(refresh_token, Config.SECRET_KEY, algorithms=['HS256'])
        new_token = generate_token(data['user_id'])  # Generate a new token
        return jsonify({'token': new_token}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Refresh token has expired!'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid refresh token!'}), 401


@routes_bp.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'

@routes_bp.route('/add_kv/', methods=['POST'])
@token_required
def add_kv(authenticated_user):
    data = request.get_json()
    key = data.get('key')
    value = data.get('value')  # Expecting a JSON string

    if key and value:
        # Check if the key already exists
        existing_kv = db.session.query(KeyValue).filter_by(key=key).first()
        if existing_kv:
            return jsonify({'error': 'Key already exists'}), 400

        new_kv = KeyValue(key=key, value=value)
        db.session.add(new_kv)
        db.session.commit()
        return jsonify({'message': 'Key-Value pair added successfully'})
    return jsonify({'error': 'Key or value is missing'}), 400

@routes_bp.route('/update_kv/', methods=['POST'])
@token_required
def update_kv(authenticated_user):
    data = request.get_json()
    key = data.get('key')
    new_value = data.get('value')  # The new JSON string to update

    if key and new_value:
        # Fetch the existing key-value pair
        existing_kv = db.session.query(KeyValue).filter_by(key=key).first()
        if existing_kv:
            # Update the value with new data
            existing_kv.value = new_value
            db.session.commit()
            return jsonify({'message': 'Key-Value pair updated successfully'})
        else:
            return jsonify({'error': 'Key does not exist'}), 404  # Key not found
    return jsonify({'error': 'Key or value is missing'}), 400  # Bad request


@routes_bp.route('/get_kvs/', methods=['GET'])
@token_required
def get_kvs(authenticated_user):
    kvs = db.session.query(KeyValue).all()
    response = jsonify([{ 'key': kv.key, 'value': kv.value } for kv in kvs])
    return response



@routes_bp.route('/delete_kv/', methods=['POST'])
@token_required
def delete_kv(authenticated_user):
    data = request.get_json()
    key = data.get('key')
    
    if key:
        existing_kv = db.session.query(KeyValue).filter_by(key=key).first()
        if existing_kv:
            db.session.delete(existing_kv)
            db.session.commit()
            return jsonify({'message': 'Key-Value pair deleted successfully'})
        else:
            return jsonify({'error': 'Key not found'}), 404  # Key not found
    return jsonify({'error': 'Key is missing'}), 400  # Bad request