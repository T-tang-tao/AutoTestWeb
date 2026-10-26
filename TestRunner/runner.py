import threading
from pathlib import Path

from TestRunner.core.TestRunner import TestRunner
from utils.ConfigLoader import ConfigLoader
from utils.LoggerManager import LoggerManager

# 定义全局变量

# 加载配置
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "configs" / "main.yml"
configLoader = ConfigLoader(path=CONFIG_PATH)
config = configLoader.get_config()
TestBed = config["TestBed"]
TestSet = config["TestSet"]

# -------------------------- 全局变量：存储用户状态（含cookie） --------------------------

USER_LOCK = threading.Lock()


def main(config_path):
    global TestBed, TestSet  # 声明使用全局变量
    # 初始化日志
    LoggerManager(config['logger'])
    # 测试执行器
    runner = TestRunner(config)
    runner.run()


if __name__ == "__main__":
    main(CONFIG_PATH)
