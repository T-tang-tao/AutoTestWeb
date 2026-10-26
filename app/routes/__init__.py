from .base_routes import base_bp
from .huixin_routes import huixin_bp


def register_routes(app):
    """注册所有路由蓝图"""
    app.register_blueprint(huixin_bp, url_prefix='/huixin')
    app.register_blueprint(base_bp)
