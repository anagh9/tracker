"""
Modular Calorie & Vices Tracker Application
Using Flask Blueprints for scalable architecture
"""

from flask import Flask
import database
from config import get_config
from routes import register_blueprints


def create_app(config_name=None):
    """
    Application factory pattern.
    Creates and configures the Flask application.
    """
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Initialize database
    database.init_db()
    
    # Register blueprints
    register_blueprints(app)
    
    return app


# Create app instance for development
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
