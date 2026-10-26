import os
from keyword import kwlist
from pathlib import Path

from Business.PrisonAssessmentSystem.API.InitAPI import InitAPI
from Business.PrisonAssessmentSystem.Data import Assessment, Process
from TestRunner.services.HttpClient import HttpClient


class PoliceApi(InitAPI):
    def __init__(self):
        super().__init__()
        self.police_client = HttpClient()

    def update_cookies(self, cookies):
        """
        更新cookies
        :param cookies:
        :return:
        """
        self.logger.debug('更新cookies完成')
        self.police_client.headers.update({'Cookie': cookies})

    def huixin_password_login(self, username, password):
        url = self._build_url("/comprehensive-assessment-system/authorize/passwordLogin")
        data = {"username": username, "password": password, "loginType": "policeManagement"}
        response = self.police_client.post(url, data=data)
        return response

    def police_package_instance_packageClose(self, packageInstanceId: str):
        """
        关闭流程实例
        :return:
        """

        params = {
            'packageInstanceId': packageInstanceId,
            "cancelReason": '自动化测试-关闭',
        }
        res = self.police_client.get(
            url=self._build_url("/comprehensive-assessment-system/crime-business/v1.0/package/instance/packageClose"),
            params=params
        )
        return res

    def police_package_instance_packageList(self, criminalId: str = None, assessment: Assessment = None, status=None,
                                            pageSize=50):
        """
        流程记录 查询
        :param pageSize:
        :param assessment:
        :param criminalId:
        :param status: 运行状态  默认审核中和进行中
        :return:
        """
        # 发送请求
        if status is None:
            status = ['RUNNING', 'AUDIT']
        params = {
            'codeOrName': criminalId,
            "status": status or ['RUNNING', 'AUDIT', 'FINISHED'],
            'folderCode': assessment.value['packageCode'] if assessment else None,
            'desc': True,
            'pageNum': 1,
            'pageSize': pageSize
        }
        res = self.police_client.get(
            url=self._build_url("/comprehensive-assessment-system/crime-business/v1.0/package/instance/packageList"),
            params=params
        )
        return res

    def police_package_instance_instanceAndTask(self, packageInstanceId: str):
        """
        流程实例 详情
        :return:
        """
        res = self.police_client.get(
            url=self._build_url(
                f"/comprehensive-assessment-system/crime-business/v1.0/instance/instanceAndTask/{packageInstanceId}"),
        )
        return res

    def police_instance_batchStart(self, assessment: Assessment, criminalId: str, easy_flow='否',
                                   trigger_mode='手动触发', packageExtend: dict = None):
        """
        发起业务包
        :param packageExtend:
        :param criminalId:
        :param easy_flow:
        :param trigger_mode:
        :param assessment: 评估包
        :return:
        """
        url = self._build_url("/comprehensive-assessment-system/crime-business/v1.0/instance/batchStart")
        json_data = [
            {
                "flowIds": assessment.value['flowIds'],
                "criminalId": criminalId,
                "packageCode": assessment.value['packageCode'],
                "triggerMode": trigger_mode,
                "easyFlow": easy_flow
            }
        ]
        res = self.police_client.post(
            url=url,
            json=json_data
        )
        return res

    def police_sheet_submit(self, taskId: str, data):
        """
        填写表单  提交
        :return:
        """
        url = self._build_url(f"/app-factory-web/app-factory/v1.0/sheet/submit/{taskId}?status=PASS")
        res = self.police_client.post(
            url=url,
            json=data
        )
        return res

    def police_criminal_base_info(self, criminalId: str):
        """
        查询罪犯基础信息
        :return:
        """
        url = self._build_url("/comprehensive-assessment-system/ficus/v1/viewPortQuery/S1/deyang/queryOverview")
        params = {
            "parameters": [
                {
                    "paramCode": "id",
                    "value": criminalId
                }
            ]
        }
        res = self.police_client.post(url, json=params)
        return res

    def police_sheet_task(self, afpTaskId: str):
        """
        查询表单详情
        :return:
        """
        url = self._build_url(f"/app-factory-web/app-factory/v1.0/sheet/task/{afpTaskId}?fixVirtualField=True")
        res = self.police_client.get(url)
        return res

    def police_sheet_task_submit(self, taskId: str):
        """
        查询表单详情
        :return:
        """
        url = self._build_url(f"app-factory-web/app-factory/v1.0/sheet/task/submit/{taskId}")
        res = self.police_client.get(url)
        return res

    def police_audit_search(self, criminalId: str = '', processId='', **kwargs):
        """
        查询罪犯审核记录
        :return:
        """
        url = self._build_url("/comprehensive-assessment-system/crime-business/v1.0/audit")
        params = {
            "focus": False,
            'isFilterPolice': True,
            "keyword": criminalId,
            "processId": processId,
            "pageNum": 1,
            "pageSize": 10,
            "status": kwargs.get("status"),
            "type": "AUDIT",
            'flowInstanceId': kwargs.get('flowInstanceId')
        }
        res = self.police_client.get(url, params=params)
        return res

    def police_audit_submit(self, auditId: str, auditData: dict):
        """
        审核提交
        :return:
        """
        url = self._build_url(
            f"/comprehensive-assessment-system/crime-business/v1.0/audit/submit/{auditId}?status=PASS")
        res = self.police_client.post(url, json=auditData)
        return res

    def police_audit_history(self, data: dict):
        """
        查询审核记录
        :return:
        """
        url = self._build_url("/comprehensive-assessment-system/onlyoffice/saveHistory")
        res = self.police_client.post(url, json=data)
        return res

    def police_reportContent(self, auditId: str):
        """
        报告内容
        :return:
        """
        url = self._build_url(f"/comprehensive-assessment-system/crime-business/v1.0/audit/{auditId}/contents")
        res = self.police_client.get(url)
        return res

    def police_reportResult(self, reportId: str):
        """
        报告结果
        :return:
        """
        url = self._build_url(f"/comprehensive-assessment-system/crime-business/v1.0/reportResult/{reportId}")
        res = self.police_client.get(url)
        return res

    def app_config(self):
        """
        应用配置
        :return:
        """
        url = self._build_url(f"/comprehensive-assessment-system/config")
        res = self.police_client.get(url)
        return res

    def app_report_detail(self, reportId: str):
        """
        报告详情
        :return:
        """
        url = self._build_url(f"/comprehensive-assessment-system/crime-business/v1.0/report/detail/{reportId}")
        res = self.police_client.get(url)
        return res

    def app_report_style(self, reportId: str):
        """
        报告样式
        :return:
        """
        url = self._build_url(
            f"/comprehensive-assessment-system/crime-business/v1.0/report/style/getStylesByReportId/{reportId}")
        res = self.police_client.get(url)
        return res

    def app_update_report(self, data: dict):
        """
        报告样式
        :return:
        """
        url = self._build_url(f"/comprehensive-assessment-system/crime-business/v1.0/report/updateReportAndStyle")
        res = self.police_client.post(url, json=data)
        return res

    def app_report_list(self):
        """
        报告样式
        :return:
        """
        url = self._build_url(f"/comprehensive-assessment-system/crime-business/v1.0/report/list?page=1&pageSize=-1")
        res = self.police_client.get(url)
        return res

    def SxjkBaseInfoReportQuery(self, criminalId: str, flowInstanceId: str):
        """
        报告样式
        :return:
        """
        url = self._build_url(
            f"/comprehensive-assessment-system/ficus/v1/viewPortQuery/S1/compa/SxjkBaseInfoReportQuery")
        data = {
            "parameters": [
                {
                    "paramCode": "criminalId",
                    "value": criminalId
                },
                {
                    "paramCode": "flowInstanceId",
                    "value": flowInstanceId
                }
            ]
        }
        res = self.police_client.post(url, json=data)
        return res

    def GtwxxBaseInfoReportQuery(self, criminalId: str, flowInstanceId: str):
        """
        报告样式
        :return:
        """
        url = self._build_url(
            f"/comprehensive-assessment-system/ficus/v1/viewPortQuery/S1/compa/GtwxxBaseInfoReportQuery")
        data = {
            "parameters": [
                {
                    "paramCode": "criminalId",
                    "value": criminalId
                },
                {
                    "paramCode": "flowInstanceId",
                    "value": flowInstanceId
                }
            ]
        }
        res = self.police_client.post(url, json=data)
        return res


if __name__ == '__main__':
    from utils.ConfigLoader import ConfigLoader

    config_path = Path(__file__).resolve().parents[4] / "configs" / "main.yml"
    ConfigLoader = ConfigLoader(path=config_path)
    username = os.environ.get("HUIXIN_USERNAME")
    password = os.environ.get("HUIXIN_PASSWORD")
    if not username or not password:
        raise RuntimeError("Set HUIXIN_USERNAME and HUIXIN_PASSWORD before running this example.")
    police_api = PoliceApi()
    response = police_api.huixin_password_login(username, password)
    police_api.update_cookies(response.headers.get('Set-Cookie'))
