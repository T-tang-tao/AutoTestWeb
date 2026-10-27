"""Flask application factory.

Importing this module is side-effect free with respect to project YAML and
logging configuration. Production startup loads the configured YAML only when
create_app() is called; tests can inject an in-memory project_config or a
prepared config_loader.
"""

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional

from flask import Flask
from flask_cors import CORS


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "main.yml"


class _DictConfigLoader:
    """In-memory config adapter for isolated application/test instances."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = deepcopy(config) if config is not None else {}
        self.config.setdefault("TestBed", {})
        self.config.setdefault("TestSet", {"test_cases": []})
        self.config.setdefault("base_dir", str(PROJECT_ROOT))
        self.config_path = None

    def get_config(self):
        return deepcopy(self.config)

    def save_test_bed(self, test_bed_data: Dict[str, Any]):
        self.config["TestBed"] = deepcopy(test_bed_data)
        return {
            "message": "TestBed配置保存成功",
            "path": None,
        }


def create_app(
    config_path: Optional[str] = None,
    test_config: Optional[Dict[str, Any]] = None,
    config_loader=None,
    project_config: Optional[Dict[str, Any]] = None,
):
    """Create an isolated Flask app with explicit project and Flask config.

    Args:
        config_path: Main YAML config path for a normal application instance.
        test_config: Flask configuration values (for example, TESTING=True).
        config_loader: Optional loader implementing config/get_config/save_test_bed.
        project_config: In-memory project config; never reads local YAML files.
    """
    if config_loader is not None and project_config is not None:
        raise ValueError("config_loader 和 project_config 不能同时提供")

    app = Flask(__name__)
    app.config["JSON_AS_ASCII"] = False
    app.config["DEFAULT_CHARSET"] = "utf-8"
    if test_config:
        app.config.update(test_config)

    if config_loader is not None:
        loader = config_loader
    elif project_config is not None:
        loader = _DictConfigLoader(project_config)
    elif app.config.get("TESTING") and config_path is None:
        # TESTING by itself must never fall back to a private local config.
        loader = _DictConfigLoader()
    else:
        from utils.ConfigLoader import ConfigLoader

        loader = ConfigLoader(path=config_path or DEFAULT_CONFIG_PATH)

    app.extensions["config_loader"] = loader

    project_settings = getattr(loader, "config", {})
    logger_config = project_settings.get("logger") if isinstance(project_settings, dict) else None
    if not app.config.get("TESTING") and isinstance(logger_config, dict):
        from utils.LoggerManager import LoggerManager

        LoggerManager.configure(logger_config)

    # Keep the existing CORS policy; changing it is outside this issue's scope.
    CORS(app, supports_credentials=True)

    from app.routes import register_routes

    register_routes(app)
    return app
