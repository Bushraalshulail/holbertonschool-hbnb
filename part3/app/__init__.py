from flask import Flask
from flask_restx import Api
from config import config
import os
from flask import send_from_directory
from app.extensions import db, jwt, bcrypt

# Absolute path to your part4 directory (two levels up from this file)
PART4_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'part4')
)
print("Serving Part 4 from:", PART4_DIR)  # helpful log line

# Import namespaces (API Blueprints)
from app.api.v1.users import api as users_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns
from app.api.v1.reviews import api as reviews_ns
from app.api.v1.auth import api as auth_ns

def create_app(config_class=config['default']):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # Register API namespaces
    api = Api(app, version='1.0', title='HBnB API', description='HBnB Application API')

    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    api.add_namespace(auth_ns, path='/api/v1/auth')

    # Serve the Part 4 frontend from /client/...
    def _client_index():
        return send_from_directory(PART4_DIR, 'index.html')

    def _client_static(filename):
        return send_from_directory(PART4_DIR, filename)

    app.add_url_rule('/client/', view_func=_client_index)
    app.add_url_rule('/client/<path:filename>', view_func=_client_static)

    return app
