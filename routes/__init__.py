"""
Routes package - Register all blueprints here
"""

from .auth import auth_bp
from .calorie import calorie_bp
from .vices import vices_bp
from .dashboard import dashboard_bp
from .onboarding import onboarding_bp

__all__ = [
    'auth_bp',
    'calorie_bp',
    'vices_bp',
    'dashboard_bp',
    'onboarding_bp',
]

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(calorie_bp, url_prefix='/calorie')
    app.register_blueprint(vices_bp, url_prefix='/vices')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(onboarding_bp)
