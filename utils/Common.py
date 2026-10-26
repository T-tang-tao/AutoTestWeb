import secrets
from datetime import datetime

import requests

from TestRunner.services.HttpClient import HttpClient
from utils.LoggerManager import LoggerManager

logger = LoggerManager().get_logger()

def generate_random_number(length=16):
    min_num = 10 ** (length - 1)
    max_num = (10 ** length) - 1
    return secrets.randbelow(max_num - min_num + 1) + min_num


def time_now():
    # 获取当前时间
    now = datetime.now()

    # 格式化时间为指定格式
    formatted_time = now.strftime("%Y-%m-%d+%H:%M:%S")
    return str(formatted_time)

def time_diff(start_time, end_time):
    start_time = datetime.strptime(start_time, "%Y-%m-%d+%H:%M:%S")
    end_time = datetime.strptime(end_time, "%Y-%m-%d+%H:%M:%S")
    time_diff = end_time - start_time
    return time_diff.total_seconds()

GLOBAL_USER_CONFIG = {}

def HuiXin_login(test_bed,refresh=False):
    """
    登录辉鑫系统
    :param test_bed:
    :param refresh: 是否刷新cookie
    :return: 登录成功返回cookie，登录失败返回None
    """
    logger.debug(f'[测试前置]初始化慧心登录信息')
    http = HttpClient()
    # GLOBAL_USER_CONFIG
    global GLOBAL_USER_CONFIG
    GLOBAL_USER_CONFIG = test_bed["HuiXin"]["users"]

    # 提取登录逻辑为内部函数，减少代码冗余
    def _login_user(type):
        """内部函数：处理单个用户的登录逻辑"""
        user_info = GLOBAL_USER_CONFIG[type]
        username = user_info['username']
        password = user_info['password']

        logger.debug(f'[慧心前置]准备登录 {type} 用户：{username}')
        url = f"{test_bed['HuiXin']['host']}/comprehensive-assessment-system/authorize/passwordLogin"
        data = {
            "username": username,
            "password": password,
            "loginType": "policeManagement"
        }
        try:
            response = http.post(url, data=data)
            # 验证登录成功并获取cookie
            if response.status_code == 201 and 'Set-Cookie' in response.headers:
                user_info['cookie'] = response.headers['Set-Cookie']
                logger.debug(f'[慧心前置]{type} 用户登录成功')
                return True
            else:
                error_msg = f'{type} 用户登录失败，状态码={response.status_code}'
                logger.error(error_msg)
                raise Exception(error_msg)

        except Exception as e:
            logger.error(f'[慧心前置]{type} 用户登录异常：{str(e)}')
            raise  # 重新抛出异常，让上层处理

    # 根据refresh参数处理不同登录逻辑
    for user_type in GLOBAL_USER_CONFIG:
        # 跳过不需要处理的用户类型
        if user_type == "criminal":
            url = f"{test_bed['HuiXin']['host']}/comprehensive-assessment-system/authorize/accessLogin"
            data = {"accessKey": GLOBAL_USER_CONFIG[user_type]["username"],
                    "loginType": "criminal"}
            try:
                res = http.post(url, data=data)
                if res.status_code == 201:
                    GLOBAL_USER_CONFIG[user_type]["cookie"] = res.headers['Set-Cookie']
                    logger.debug(f'罪犯登录成功 --  {GLOBAL_USER_CONFIG[user_type]["username"]} ')
                else:
                    logger.error(f'罪犯登录失败，状态码: {res.status_code}')
            except Exception as e:
                logger.error(f'罪犯登录请求出错: {e}')
            continue

        # 判断是否需要登录
        need_login = (refresh
                      or 'cookie' not in GLOBAL_USER_CONFIG[user_type])

        if need_login:
            _login_user(user_type)

    logger.debug(f"环境用户登录信息已更新: {', '.join(GLOBAL_USER_CONFIG)}")
    return GLOBAL_USER_CONFIG
