# Business/PrisonAssessmentSystem/PoliceSystem.py
import json
from functools import wraps
from logging import Logger
from pathlib import Path

from Business.PrisonAssessmentSystem.API.HuiXin.PoliceApi import PoliceApi
from Business.PrisonAssessmentSystem.Data import HUIXIN_USER, Assessment, ProcessNode, Process
from Business.PrisonAssessmentSystem.Service.HuiXinService.InitHuiXin import InitHuiXin, global_retry
from TestRunner.core.Base import StepStatus


def auth_login():
    """
    警察自动登录装饰器工厂，处理用户切换与登录状态维护
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                if 'user_type' in kwargs:
                    user_type = kwargs.pop('user_type')
                elif self.current_user is not None:
                    user_type = self.current_user
                else:
                    user_type = HUIXIN_USER.prison_police
                self.current_user = user_type
                self.service.police_client.headers["Cookie"] = self.users[user_type.name]['cookie']
                # 执行被装饰的函数
            except Exception as e:
                self.logger.error(f'auth_login 装饰器 失败：{str(e)}')
                raise
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


class PoliceService(InitHuiXin):
    def __init__(self):
        super().__init__()
        self.service = PoliceApi()
        self.current_process_information = {}
        self.init_user_cookie()
        self.current_user = HUIXIN_USER.prison_police

    def init_user_cookie(self):
        """
        初始化用户cookie  前置条件
        :return:
        """
        self.logger.debug(f"[业务层初始化]初始化用户cookie开始")
        for user_type in self.users:
            if user_type == 'criminal':
                continue
            user = self.users[user_type]
            res = self.service.huixin_password_login(username=user['username'], password=user['password'])
            user['cookie'] = res.headers['Set-Cookie']
        self.service.update_cookies(self.users['prison_police']['cookie'])
        self.logger.debug(f"初始化用户cookie完成 {self.users}")

    def huixin_police_login(self, user_type: HUIXIN_USER):
        self.logger.debug(f'开始登录 {user_type.name}')
        user = self.users[user_type.name]
        try:
            self.service.huixin_password_login(username=user['username'], password=user['password'])
        except Exception as e:
            self.logger.error(f'登录 {user_type.name} 失败：{str(e)}')
            raise

    @auth_login()
    def police_close_package(self, assessment: Assessment = None, criminalId: str = None):
        """
        关闭罪犯所有业务包
        :param criminalId:
        :param assessment: 评估小包 不传默认关闭所有业务包
        :return:
        """
        try:
            criminalId = criminalId or self.users['criminal']['id']
            self.logger.debug(f'查询罪犯criminalId={criminalId} 进行中 {assessment.name if assessment else '所有'} ')
            response = self.service.police_package_instance_packageList(criminalId=criminalId,
                                                                        assessment=assessment).json()
            assessmentList = response['resultList']
            self.logger.debug(f'查询罪犯业务包结果 {assessmentList}')
            if assessmentList:
                for assessment in assessmentList:
                    self.service.police_package_instance_packageClose(packageInstanceId=assessment['id'])
                    self.logger.debug(f'关闭罪犯业务包 {assessment["id"]}')
            else:
                self.logger.debug(f'罪犯 {criminalId} 没有进行中业务包 {assessment.name if assessment else ''}')
        except Exception as e:
            self.logger.error(f'关闭罪犯所有业务包失败：{str(e)}')
            raise Exception(f'关闭罪犯所有业务包失败：{str(e)} {assessment.name if assessment else '所有'}')

    @auth_login()
    def police_begin_assessment(self, assessment: Assessment, criminalId: str = None):
        """
        发起业务包
        :param criminalId:
        :param assessment: 评估包
        :return:
        """
        try:
            packageExtend = None
            if assessment == Assessment.中期_认罪悔改表现评估:
                packageExtend = {
                    'packageExtend': {
                        "ohYzku6f7": {
                            "select_item": "无上述情形",
                            "timeSection": "2025-09-19,2025-09-20"
                        }
                    }
                }
            res = self.service.police_instance_batchStart(assessment=assessment,
                                                          criminalId=criminalId or self.users['criminal']['id'],packageExtend=packageExtend)
            if res.status_code == 200:
                res = res.json()
                self.logger.debug(f'发起业务包 {assessment.name} 成功')
                self.current_process_information['successData'] = res['content'][0]['successData'][0]
            else:
                self.logger.error(f'发起业务包 {assessment.name} 失败：{res.text}')
                raise Exception(f'发起业务包 {assessment.name} 失败：{res.text}')
        except Exception as e:
            self.logger.error(f'发起业务包 {assessment.name} 失败：{str(e)}')
            raise Exception(f'发起业务包 {assessment.name} 失败：{str(e)}')

    @auth_login()
    def police_write_sheet_submit(self, data):
        """
        填写表单  提交  需要先执行 填写量表在进行中
        :return:
        """
        afpTaskId = self.current_process_information['currentNode']['afpTaskId']
        res = self.service.police_sheet_submit(taskId=afpTaskId, data=data)
        if res.status_code == 200:
            self.logger.debug(f'填写表单  提交 成功')
        else:
            self.logger.error(f'填写表单  提交 失败：{res.text}')
            raise Exception(f'填写表单  提交 失败：{res.text}')

    @auth_login()
    def get_current_process_information(self, assessment: Assessment):
        """
        审核
        :return:
        """
        self.logger.debug(f'查询 罪犯 {self.users['criminal']['id']} 当前流程信息 {assessment.name}')
        packageId = self.current_process_information['successData']['packageInstanceId']
        res = self.service.police_package_instance_instanceAndTask(packageInstanceId=packageId).json()
        successData = self.current_process_information['successData']
        self.current_process_information = {
            'criminalId': self.users['criminal']['id'],
            'criminalName': self.users['criminal']['name'],
            'packageName': assessment.name,
            'processNode': assessment.value,
            'packageId': packageId,
            'packageInstanceId': packageId,
            'packageInstanceDetail': res['content'],
            'successData': successData,
        }
        return self.current_process_information

    @global_retry()
    @auth_login()
    def check_current_process_information(self, assessment: Assessment, status: StepStatus,
                                          processNode: ProcessNode = None, sonPackage=None):
        self.logger.debug(
            f'校验 罪犯 {self.users['criminal']['id']} 流程信息 {assessment.value['folderName']} 节点 {processNode.name if processNode else ''} 预期状态 {status.name}')
        info = self.get_current_process_information(assessment)

        match_node = False
        for detail in info['packageInstanceDetail']:
            if not processNode:
                assert detail.get(
                    'status') == status.name, f'当前流程 {assessment.name} 预期状态 {status.name} 实际状态 {detail.get("status")} 通过'
                self.logger.debug(
                    f'当前流程 {assessment.name} 预期状态 {status.name} 实际状态 {detail.get("status")} 通过')
                match_node = True
            elif detail.get('flowProcessName') == assessment.value['folderName']:
                for task in detail.get('flowTaskPO', []):
                    if task.get('flowProcessStepName') == processNode.name:
                        match_node = True
                        assert task.get(
                            'status') == status.name, f'当前流程节点 {detail} {processNode.name} 预期状态 {status.name} 实际状态 {task.get("status")}'
                        self.logger.debug(
                            f'当前流程节点 {detail} {processNode.name} 预期状态 {status.name} 实际状态 {task.get("status")} 通过')
                        self.logger.debug(f'更新当前节点信息 {task} 详情')
                        self.current_process_information['currentNode'] = task
                        # 获取表单详情
                        res = self.service.police_sheet_task(
                            self.current_process_information['currentNode']['afpTaskId'])
                        self.current_process_information['currentNode']['afpTaskDetail'] = res.json()
                        self.current_process_information['currentNode']['packageInfo'] = info
                        return
            else:
                continue
        if not match_node and 'currentNode' not in self.current_process_information:
            self.logger.error(f'当前流程节点 {processNode.name} 未执行到节点 {processNode.name} 重试')
            raise

    @auth_login()
    def police_search_criminal(self, criminalId: str):
        """
        查询罪犯信息
        :param criminalId:
        :return:
        """
        res = self.service.police_criminal_base_info(criminalId=criminalId).json()['resultList'][0]
        if 'baseinfo' in res:
            self.criminal_information = res
            return res
        else:
            raise Exception(f'查询罪犯信息失败：{res.text}')

    @global_retry()
    @auth_login()
    def police_audit_submit(self, data: dict, process: Process = None):
        """
        审核提交
        :return:
        """
        criminalId = self.users['criminal']['id']
        self.logger.debug(f'{self.current_user}查询审核记录 {criminalId} {process}')
        try:
            res = self.service.police_audit_submit(auditId=data.get('auditId'), auditData=data.get('auditData'))
            assert res.status_code == 200, f'{self.current_user}审核提交 {criminalId} 失败：{res.text} 重试'
            if 'saveData' in data:
                res = self.service.police_audit_history(data.get('saveData'))
                assert res.status_code == 200, f'保存审核记录 {criminalId} 失败：{res.text} 重试'
            self.logger.debug(f'{self.current_user}审核提交 {criminalId} 成功')
        except Exception as e:
            self.logger.error(f'{self.current_user}审核提交 {criminalId} 失败：{str(e)}')
            raise Exception(f'{self.current_user}审核提交 {criminalId} 失败：{str(e)} ')

    @global_retry()
    @auth_login()
    def police_audit_init(self, process: Process = None):
        """
        审核提交
        :return:
        """
        criminalId = self.users['criminal']['id']
        self.logger.debug(f'{self.current_user}查询审核记录 {criminalId} {process}')
        try:
            res = self.service.police_audit_search(criminalId, processId=process.value)
            assert res.status_code == 200, f'{self.current_user}查询审核记录 {criminalId} 失败：{res.text} 重试'
            res = res.json()
            if res['resultList']:
                return res
            else:
                raise Exception(f'{self.current_user}查询审核记录失败：{res.text} 重试')
        except Exception as e:
            self.logger.error(f'{self.current_user}审核提交 {criminalId} 失败：{str(e)}')
            raise Exception(f'{self.current_user}审核提交 {criminalId} 失败：{str(e)} ')

    @global_retry()
    @auth_login()
    def police_get_audit_info(self, process: Process = None):
        data = {}
        criminalId = self.users['criminal']['id']
        self.logger.debug(f'{self.current_user}查询审核记录 {criminalId} {process}')
        try:
            res = self.service.police_audit_search(criminalId, processId=process.value, status='NEW')
            assert res.status_code == 200, f'{self.current_user}查询审核记录 {criminalId} 失败：{res} 重试'
            res = res.json()
            if res['resultList']:
                data['flowInstanceId'] = res['resultList'][0]['flowInstanceId']
                data['auditId'] = res['resultList'][0]['id']
                reportContent = self.service.police_reportContent(auditId=data['auditId'])
                assert reportContent.status_code == 200, f'{self.current_user}查询报告内容 {data['auditId']} 失败：{reportContent.text} 重试'
                data['reportContent'] = reportContent.json()
                reportId = data['reportContent'][0]['sourceId']
                reportResult = self.service.police_reportResult(reportId=reportId)
                assert reportResult.status_code == 200, f'{self.current_user}查询报告结果 {reportId} 失败：{reportResult.text} 重试'
                report = reportResult.json()['content']
                data['reportResult'] = report
                self.current_process_information['auditDetail'] = data
                return data
            else:
                raise Exception(f'{self.current_user}查询审核记录失败：重试')
        except Exception as e:
            self.logger.error(f'{self.current_user}审核提交 {criminalId} 失败：{str(e)}')
            raise Exception(f'{self.current_user}审核提交 {criminalId} 失败：{str(e)} ')


# 示例使用
if __name__ == "__main__":
    from utils.ConfigLoader import ConfigLoader

    config_path = Path(__file__).resolve().parents[4] / "configs" / "main.yml"
    ConfigLoader = ConfigLoader(path=config_path)
    police_system = PoliceService()
    police_system.huixin_police_login(HUIXIN_USER.prison_police)
