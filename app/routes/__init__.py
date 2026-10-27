from .api_routes import api_bp
from .base_routes import base_bp
from .huixin_routes import huixin_bp


def register_routes(app):
    """Register the versioned generic API and legacy route aliases."""
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(huixin_bp, url_prefix="/huixin")
    app.register_blueprint(base_bp)
