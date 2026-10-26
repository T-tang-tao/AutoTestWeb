from Business.PrisonAssessmentSystem.API.InitAPI import InitAPI
from TestRunner.services.HttpClient import HttpClient


class CriminalApi(InitAPI):
    def __init__(self):
        super().__init__()
        self.criminal_client = HttpClient()

    def criminal_sheet_submit(self, afpTaskId, data):
        """
        :param afpTaskId:
        :param data:
        :return:
        """
        url = self._build_url(f'/app-factory-web/app-factory/v1.0/sheet/submit/{afpTaskId}')
        res = self.criminal_client.post(url, json=data)
        return res

    def criminal_query_taskV2(self, focus=False, needCount=True, page=1, scope="WEB",
                              size=10, type="TASK"):
        """
        罪犯待填写流程
        :param focus: 布尔值，是否聚焦
        :param needCount: 布尔值，是否需要计数
        :param page: 页码
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
        url = self._build_url('/comprehensive-assessment-system/crime-business/v1.0/task/queryV2')
        res = self.criminal_client.get(url, params=params)
        return res

    def criminal_sheet_task(self, task_id):
        """
        罪犯填写写sheet前的数据
        :return:
        """
        url = self._build_url(f'/app-factory-web/app-factory/v1.0/sheet/task/{task_id}')
        res = self.criminal_client.get(url)
        return res
