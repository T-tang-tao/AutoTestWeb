import time

from Business.PrisonAssessmentSystem.API import Ficus, HuiXin
from Business.PrisonAssessmentSystem.API.InitAPI import global_retry
from Business.PrisonAssessmentSystem.Data import HuiXin_PROCESS_STATUS, Assessment, ProcessNode, ProcessStepStatus
from Business.PrisonAssessmentSystem.Service.JiaXin.JiaXin import JiaXinService
from TestRunner.core.Base import Base
from TestRunner.services.DataBaseClient import DataBaseClient
from Business.PrisonAssessmentSystem.Service.HuiXinService import HuiXinService
from utils.ConfigLoader import ConfigLoader


class CriminalBaseJiaXin(Base):
    def __init__(self, **kwargs):
        super(CriminalBaseJiaXin, self).__init__()
        self.logger.info("=====初始化罪犯测试框架=====")
        self.params = kwargs.get('params')

        database_config = ConfigLoader().get_config()["TestBed"]["database"]
        self.db = DataBaseClient(
            host=database_config["host"],
            user=database_config.get("user", database_config.get("username")),
            password=database_config["password"],
            port=int(database_config.get("jiaxin_port", database_config["port"])),
            database=database_config.get("database", "criminal_business"),
        )
        # 注册业务
        self.ficus_app = Ficus()

        self.task_information = {}
        self.logger.info("=====初始化罪犯测试框架完成=====")

        self.huixin_server = JiaXinService()
        self.huixin_server.users = kwargs.get('user_cookie')

    def setUp(self) -> None:
        pass

    def init_criminal_info(self, criminalId: str) -> None:
        # 初始化罪犯信息
        self.logger.info("初始化罪犯信息")
        self.huixin_server.police_search_criminal(criminalId=criminalId)

    def check_process_instance(self, status: HuiXin_PROCESS_STATUS, assessment: Assessment = Assessment):
        """
        :param status:
        :param assessment:
        :return:
        """
        max_time = 30
        start_time = time.time()
        resultList = None
        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > max_time:
                raise AssertionError("算法在 30 秒内执行完成，请查看任务")
            res = self.huixin_app.police_process_record_search(
                criminalId=self.criminalId)
            if res['resultList'] is None:
                time.sleep(2)
                continue
            else:
                resultList = res['resultList'][0]
                assert resultList['folderName'] == assessment.value['folderName'], "业务包名称不对应"
                assert resultList['folderCode'] == assessment.value['packageCode'], "业务包 code 不对应"
                assert resultList['criminalId'] == self.criminalId, "罪犯 ID 不对应"
                assert resultList['status'] == status.name, "流程状态不正确"
                break
        if resultList is None:
            self.logger.error('算法执行超时：30s')
            raise AssertionError('算法执行超时：30s')





    @global_retry()
    def check_audit_status(self):
        flowId = self.huixin_server.current_process_information['auditDetail']['flowInstanceId']
        res = self.huixin_server.service.police_audit_search(flowId=flowId)
        assert res.status_code == 200, '审核任务查询失败'
        auditList = res.json()['resultList']
        audit_pass = False
        for audit in auditList:
            if audit['id'] == self.huixin_server.current_process_information['auditDetail']['auditId']:
                assert audit['status'] == ProcessStepStatus.PASS.name, f'审核流程校验不通过  预期{ProcessStepStatus.PASS.name} 实际{audit["status"]}'
                audit_pass = True
                break
        if not audit_pass:
            self.logger.error(f'未找到审核任务：{self.huixin_server.current_process_information["auditDetail"]["auditId"]}  重试中...')
            raise AssertionError(f'未找到审核任务：{self.huixin_server.current_process_information["auditDetail"]["auditId"]}')


    @global_retry()
    def check_package_process_status(self):
        packageId = self.huixin_server.current_process_information['successData']['packageInstanceId']
        res = self.huixin_server.service.police_package_instance_instanceAndTask(packageInstanceId=packageId)
        assert res.status_code == 200, '流程实例查询失败'
        assert res.json()['content'][0]['status'] == ProcessStepStatus.FINISHED.name, '流程状态与预期不符'
