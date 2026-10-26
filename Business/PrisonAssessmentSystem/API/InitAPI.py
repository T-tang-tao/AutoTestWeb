from functools import wraps
from tenacity import stop_after_attempt, wait_fixed, retry

from Business.PrisonAssessmentSystem.Data import HUIXIN_USER
from utils import Common
from utils.ConfigLoader import ConfigLoader
from utils.LoggerManager import LoggerManager


def url_path(path):
    """
    拼接url 装饰器
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            url = self.base_url + path
            return func(self, url, *args, **kwargs)

        return wrapper

    return decorator


def police_login(user_type=None):
    """
    警察自动登录装饰器工厂，处理用户切换与登录状态维护
    :param user_type: 目标用户类型，未指定则使用被装饰方法传入的user_type或当前用户
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # 用户
            final_user_type = kwargs.pop('user_type', user_type) or self.current_user or HUIXIN_USER.prison_police
            self.current_user = final_user_type  # 同步更新当前用户状态
            users = Common.GLOBAL_USER_CONFIG
            if not users:
                users = Common.HuiXin_login(self.test_bed)
            target_user = users[final_user_type.name]
            target_cookie = target_user['cookie']

            self.police_client.headers["Cookie"] = target_cookie
            # 执行被装饰的函数
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

def criminal_login():
    """
    自动登录装饰器工厂，可传入 user_type 参数
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # 检查是否已登录（通过检查 Cookie 是否存在）
            if not self.isLogin:
                self.logger.info("罪犯未登录，正在自动登录...")
                self.huixin_criminal_login()
            # 执行目标方法，传递所有参数
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


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


class InitAPI:
    def __init__(self):
        self.logger = LoggerManager().get_logger()
        self.logger.debug("初始化接口层 InitAPI 类...")

        self.test_bed = ConfigLoader().get_config()['TestBed']
        self.base_url = self.test_bed['HuiXin']['host']

        self.huixin_base_url = self.test_bed['HuiXin']['host']

        self.users = self.test_bed['HuiXin']['users']
        self.logger.debug(f"初始化完成")

    def _build_url(self, path: str) -> str:
        """构建完整的URL"""
        return f"{self.base_url}{path}"

    # @staticmethod
    # def result_list_choose(result_list, assessment: Assessment, son_assessment: Assessment):
    #     folderCode = assessment.in_prison_assessment.value['packageCode']
    #     sonCode = assessment.in_prison_criminal_basic_information.value['packageCode']
    #     for i in result_list:
    #         if i['folderCode'] == folderCode:
    #             for j in i['children']:
    #                 if j['folderCode'] == sonCode:
    #                     return j['id']
