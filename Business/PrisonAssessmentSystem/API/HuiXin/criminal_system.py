import time
from functools import wraps

from Business.PrisonAssessmentSystem.API.InitAPI import InitAPI, police_login, global_retry, criminal_login, url_path
from TestRunner.services.HttpClient import HttpClient


class CriminalSystem(InitAPI):
    def __init__(self):
        super().__init__()
        self.criminal_client = HttpClient()
        self.isLogin = False

        self.criminal_current_process={}
        self.config = {}

    def huixin_criminal_login(self, criminalId=None):
        url = f"{self.base_url}/comprehensive-assessment-system/authorize/accessLogin"
        data = {"accessKey": criminalId or self.users['criminal']['id'],
                "loginType": "criminal"}
        try:
            res = self.criminal_client.post(url, data=data)
            if res.status_code == 201:
                self._criminalLogin = True
                self.criminal_client.headers["Cookie"] = res.headers['Set-Cookie']
                self.logger.debug(f'罪犯登录成功 --  {self.users['criminal']['id']} ')
            else:
                self.logger.error(f'罪犯登录失败，状态码: {res.status_code}')
        except Exception as e:
            self.logger.error(f'罪犯登录请求出错: {e}')

    @global_retry()
    @criminal_login()
    @url_path('/comprehensive-assessment-system/crime-business/v1.0/task/queryV2')
    def criminal_task_query_v2(self, url, focus=False, needCount=True, page=1, scope="WEB",
                               size=10, type="TASK"):
        """
        罪犯待填写流程
        :param url: 拼接后的完整 URL
        :param focus: 布尔值，是否聚焦
        :param needCount: 布尔值，是否需要计数
        :param page: 页码
        :param prisonAreas: 监区名称
        :param scope: 范围
        :param size: 每页大小
        :param type: 任务类型
        :return: 响应的 JSON 数据或 None
        """
        params = {
            'focus': focus,
            'needCount': needCount,
            'page': page,
            'scope': scope,
            'size': size,
            'type': type
        }
        self.logger.debug(f'请求参数{params}')
        try:
            res = self.criminal_client.get(url, params=params)
            self.logger.debug(res)
            return res.json()
        except Exception as e:
            self.logger.error(f'task_query_v2 请求出错: {e}')
            return None

    @criminal_login()
    @url_path('/comprehensive-assessment-system/config')
    def criminal_config(self, url):
        res = self.criminal_client.get(url)
        self.config = res.json()
        return res.json()

    @criminal_login()
    @url_path(
        '/comprehensive-assessment-system/crime-business/v1.0/task/queryV2?focus=false&needCount=true&page=1&scope=WEB&size=10&type=TASK')
    def criminal_task_list(self, url):
        """
        查询罪犯任务列表
        :param url:
        :return:
        """
        res = self.criminal_client.get(url).json()['resultList']
        self.task_list = res
        self.logger.debug(f'罪犯任务列表{self.task_list}')
        return res

    @criminal_login()
    @url_path('/app-factory-web/app-factory/v1.0/sheet/submit/')
    def criminal_sheet_submit(self, url, data):
        """
        1、获取父包id
        2、通过父包id查询子包、流程
        3、子包查询流程

        :param url:
        :param kwargs:
        :return:
        """
        id = data.pop('afpTaskId')
        res = self.criminal_client.post(url + id, json=data)
        if res.status_code != 200:
            raise AssertionError('更新表单失败')

    @criminal_login()
    @url_path('/app-factory-web/app-factory/v1.0/sheet/task/')
    def criminal_sheet_task(self, url, taskId: str):
        """
        :param url:
        :param taskId:
        :return:
        """
        time.sleep(2)
        params = {'fixVirtualField': True}
        res = self.criminal_client.get(url + taskId, params)
        return res.json()


if __name__ == "__main__":
    c = CriminalSystem()
    # p.police_init_body_heart_table()
    # p.police_search_criminal_basic_information()
    c.criminal_task_query_v2()
