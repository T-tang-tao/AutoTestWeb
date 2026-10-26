from functools import wraps

from TestRunner.services.HttpClient import HttpClient
from utils.ConfigLoader import ConfigLoader
from utils.LoggerManager import LoggerManager


def auth_login(func):
    """
    自动登录装饰器，确保调用方法时已登录。
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # 检查是否已登录（通过检查 Cookie 是否存在）
        if self.ficus_client.headers == "":
            self.logger.info("未登录，正在自动登录...")
            self.ficus_login()
        # 执行目标方法
        return func(self, *args, **kwargs)

    return wrapper


class Ficus:
    def __init__(self):
        self.logger = LoggerManager().get_logger()

        self.main_config = ConfigLoader().config

        self.TestBed = self.main_config['TestBed']

        self.ficus_config = self.TestBed['ficus']
        self.base_url = self.ficus_config['host']
        self.login_url = self.ficus_config['login_url']
        self.ficus_client = HttpClient()

    def ficus_login(self):
        """登录并保存 Cookie"""
        data = {
            "parentKey": "admin",
            "redirect_uri": f"{self.base_url}/sobey-ficus-pi/authorize/SSOCheckUser",
            "client_id": "sobey_ficus_pi",
            "username": f"{self.ficus_config['username']}",
            "password": f"{self.ficus_config['password']}"
        }
        res = self.ficus_client.post(self.login_url + '/login', data=data, content_type='form')

        JSESSIONID = res.cookies['JSESSIONID']
        res_json = res.json()
        self.ficus_client.cookies = f"JSESSIONID={JSESSIONID};lingyun_www_logged_in=yes;__login_type__=mg"
        self.ficus_client.headers.update({"Cookie": self.ficus_client.cookies})

        if "redirect_uri" in res_json:
            code = res_json['redirect_uri'].split('=')[-1]
            res_check = self.ficus_client.get(
                f'{self.base_url}/sobey-ficus-pi/authorize/SSOCheckUser?code={code}',
                allow_redirects=False  # 禁用自动重定向
            )
            # 设置 cookie
            Set_Cookie = res_check.headers.get("Set-Cookie")
            self.ficus_client.headers.update(
                {"Cookie": f"JSESSIONID={JSESSIONID};lingyun_www_logged_in=yes;__login_type__=mg;{Set_Cookie}"})

    @auth_login
    def zfz_data_organize(self, criminalId, assessment_id):
        # 请求体
        data = {
            "flowInstanceId": assessment_id,
            "criminalId": criminalId,
            "projectCode": "deyang"
        }
        res = self.ficus_client.post(
            self.base_url + '/sobey-ficus-pi/sobeyficus/v1/jobschedule/S1/deyang/ja_zfz_data_organize', json=data)
        return res


if __name__ == '__main__':
    f = Ficus()
