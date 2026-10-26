from tenacity import stop_after_attempt, wait_fixed, retry

from utils.ConfigLoader import ConfigLoader
from utils.LoggerManager import LoggerManager

# 默认重试配置（可根据需要修改）
DEFAULT_RETRY_CONFIG = {
    'stop': stop_after_attempt(30),  # 最多重试5次
    'wait': wait_fixed(2),  # 每次等待2秒
    'reraise': True,  # 重试后仍抛出最终异常
}
def global_retry(**kwargs):
    """
    全局重试装饰器，整合常用的重试配置
    :param kwargs: 可选参数，用于覆盖默认配置
    """

    # 合并默认配置和用户自定义配置
    config = {**DEFAULT_RETRY_CONFIG, **kwargs}
    return retry(**config)

class InitHuiXin:
    def __init__(self):
        self.logger = LoggerManager().get_logger()
        self.logger.debug("初始化业务层 InitService 类...")
        self.test_bed = ConfigLoader().get_config()['TestBed']
        self.users = self.test_bed['HuiXin']['users']

        self.huixin_base_url = self.test_bed['HuiXin']['host']
        self.logger.debug(f"初始化业务层完成")
