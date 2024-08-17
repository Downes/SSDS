from flask import Flask,request, jsonify, redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS
from flask_bootstrap import Bootstrap
from markupsafe import escape
from functools import wraps
from config import Config  
import os

app = Flask(__name__)
bootstrap = Bootstrap(app)
CORS(app)  # Enable CORS for all domains on all routes


# Database configuration
app.config.from_object('config.Config')
db = SQLAlchemy(app)

# Login configuration
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

from models import *
from routes import routes_bp
from auth import *
from forms import *

app.register_blueprint(routes_bp)
app.register_blueprint(auth_bp)    

# Initialize the database tables
with app.app_context():
    db.create_all()

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User  # Import here to avoid circular dependencies
    return User.query.get(int(user_id))

# Dynamically bind SQLAlchemy to different databases per user
@app.before_request
def before_request():
    # List of paths that should be exempt from database binding
    exempt_paths = ['/login', '/register', '/logout']
    # Check if the current request path is in the exempt list
    if request.path in exempt_paths:
        return  # Skip binding database for these routes
    
    # Proceed with database binding for authenticated users on other routes
    if current_user.is_authenticated and current_user.db_uri:
        print(f"Binding database for user: {current_user.username}")
        print(f"Database URI: {current_user.db_uri}")

        # Create a new engine for the user-specific database
        engine = create_engine(current_user.db_uri)

        # Bind the session to this engine
        db.session.remove()  # Remove the current session to avoid conflicts
        db.session.configure(bind=engine)  # Reconfigure the session with the new engine


@app.teardown_appcontext
def teardown_db(exception=None):
    from flask import g
    if hasattr(g, 'user_db'):
        g.user_db.session.remove()  # Properly close the session



@app.route('/routes/', methods=['GET'])
def routes():
    output = []
    for rule in app.url_map.iter_rules():
        output.append(f"{rule}")
    return jsonify(output)


if __name__ == '__main__':
    app.run(debug=True)




