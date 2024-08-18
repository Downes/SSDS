from flask import Blueprint, current_app, request, redirect, render_template, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user
from models import User
from flask_cors import CORS
from app import login_manager
from utils import login_required_json  # Import the decorator from utils.py
from utils import generate_token  # Import the token generation function
from forms import *
from werkzeug.security import generate_password_hash, check_password_hash
from app import db  # Import the db instance from app.py
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from flask import current_app

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


from flask import current_app  # Add this import at the top of your auth.py

@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    next_page = request.args.get('next')  # Capture the 'next' parameter
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        
        # Define the user's database URI
        user_db_uri = f'sqlite:////var/www/webroot/ROOT/{form.username.data}_db.db'
        user = User(username=form.username.data, password=hashed_password, db_uri=user_db_uri)
         
        try:
            db.session.add(user)
            db.session.commit()

            # Create the user's database
            engine = create_engine(user_db_uri)
            if not database_exists(engine.url):
                create_database(engine.url)

            # Manually manage the raw connection for PRAGMA execution
            raw_conn = engine.raw_connection()
            try:
                cursor = raw_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                raw_conn.commit()
            finally:
                cursor.close()
                raw_conn.close()

            # Use the models to create tables directly in the new user's database
            with current_app.app_context():  # Use current_app instead of app
                db.metadata.create_all(bind=engine)

            flash('Your account has been created! You are now able to log in.', 'success')
            
            # Automatically log in the user after registration or redirect to login page
           
            token = generate_token(user.id)
            login_user(user)  # Uncomment to log the user in automatically
            if next_page:
                # Redirect to the next page with the token as a URL parameter
                return redirect(f'{next_page}?token={token}&username={user.username}')
            return jsonify({'token': token, 'username': user.username}), 200  # Fallback to 


        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            
    return render_template('register.html', title='Register', form=form)






@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)  # Log the user in
            flash('Login successful', 'success')
            token = generate_token(user.id)

            # Get the referring page URL from the `next` parameter
            next_page = request.args.get('next') or request.form.get('next')
            if next_page:
                # Redirect to the next page with the token as a URL parameter
                return redirect(f'{next_page}?token={token}&username={user.username}')
            return jsonify({'token': token, 'username': user.username}), 200  # Fallback to returning the token in JSON
        else:
            flash('Login failed. Please check your username and password.', 'danger')
            return jsonify({'error': 'Invalid username or password'}), 401
    # If the form is not valid, return the form errors as JSON
    return render_template('login.html', title='Login', form=form)

@auth_bp.route("/logout")
@login_required_json
def logout():
    logout_user()  # This logs the user out
    flash('You have been logged out.', 'success')
    return jsonify({'message': 'Logout successful'}), 200



@auth_bp.route('/login_status', methods=['GET'])
def login_status():
    if current_user.is_authenticated:
        return jsonify({
            'logged_in': True,
            'username': current_user.username
        }), 200
    else:
        return jsonify({
            'logged_in': False
        }), 200

@auth_bp.route('/status', methods=['GET'])
def status():
    if current_user.is_authenticated:
        return render_template('status.html', username=current_user.username)
    else:
        return render_template('status.html', username=None)

