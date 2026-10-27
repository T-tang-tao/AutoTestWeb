from flask import Flask
from flask_cors import CORS
from pathlib import Path


from utils.ConfigLoader import ConfigLoader
from utils.LoggerManager import LoggerManager

# 测试框架运行的配置文件路径
PROJECT_ROOT = Path(__file__).resolve().parents[1]
config_path = PROJECT_ROOT / "configs" / "main.yml"
# 加载配置
ConfigLoader = ConfigLoader(config_path)
config = ConfigLoader.config
# TestBed = config["TestBed"]
# TestSet = config["TestSet"]

# 初始化日志
LoggerManager(config['logger'])

# 自动化框架根目录
AutoTestFramework_Root = str(PROJECT_ROOT)


def create_app():
    app = Flask(__name__)

    # 配置 CORS（允许所有域名跨域）
    CORS(app, supports_credentials=True)

    app.config['JSON_AS_ASCII'] = False
    app.config['DEFAULT_CHARSET'] = 'utf-8'
    # 初始化扩展
    # db.init_app(app)
    # migrate.init_app(app, db)

    # 注册蓝图
    from app.routes import register_routes
    register_routes(app)

    return app
