import json
import time

from Business.PrisonAssessmentSystem.API.InitAPI import InitAPI, police_login, global_retry
from Business.PrisonAssessmentSystem.Data import HUIXIN_USER, Assessment, HuiXin_PROCESS_STATUS, ProcessNode, Process
from TestRunner.core.Base import StepStatus
from TestRunner.services.HttpClient import HttpClient
from utils.Common import generate_random_number


class PoliceSystem(InitAPI):
    def __init__(self):
        super().__init__()
        self.police_client = HttpClient()
        self.current_user = HUIXIN_USER.prison_police
        self.package_list = []
        self.process_information = []
        self.current_process_information = {
            'id': '',  # 当前进行中父包流程ID
            'task': '',  # 罪犯任务  police_assessment_process_search更新
            'node': {},  # 节点信息
            'initiate_process_res': {}  # 发起流程返回结果
        }

    def _build_url(self, path: str) -> str:
        """构建完整的URL"""
        return f"{self.base_url}{path}"

    def _test_login(self,cookie):
        """测试登录"""
        self.logger.debug("测试登录")
        http_client = HttpClient()
        http_client.headers['Cookie'] = cookie
        res = http_client.get(self._build_url("/comprehensive-assessment-system/crime-business/v1.0/infer/index"))
        if res.status_code == 200:
            return True
        else:
            return False

    def huixin_police_login(self, user_type: HUIXIN_USER):
        self.logger.debug(f'开始登录 {user_type.name}')
        user = self.users[user_type.name]
        url = self._build_url("/comprehensive-assessment-system/authorize/passwordLogin")
        data = {"username": user['username'], "password": user['password'], "loginType": "policeManagement"}

        try:
            res = self.police_client.post(url, data=data)
            if res.status_code == 201:
                cookie = res.headers['Set-Cookie']
                self.current_user = user_type
                self.logger.debug(f' 登录成功 - {self.current_user.value}:{user}')
                return cookie
            self.logger.error(f'{user_type.name} 登录失败，状态码: {res.status_code}')
        except Exception as e:
            self.logger.error(f'登录异常: {e}')
            return False

    def is_user_logged_in(self, user_type: HUIXIN_USER) -> bool:
        # 判断是否登录
        return (
                user_type.name in self.users and
                self.users[user_type.name]['cookie'] != ''
        )

    def switch_to_user(self, user_type: HUIXIN_USER):
        # 切换用户
        if self.is_user_logged_in(user_type):
            self.police_client.headers["Cookie"] = self.users[user_type.name]['cookie']
            self.current_user = user_type

            self.logger.info(f"已切换到用户 {user_type.name}")
        else:
            self.logger.warning(f"用户 {user_type.name} 未登录，将尝试登录")
            self.huixin_police_login(user_type)

    @police_login()
    def police_search_zfz_factory(self, criminalId, assessment_id):
        url = self._build_url("/comprehensive-assessment-system/ficus/v1/viewPortQuery/S1/deyang/RecrimeFactorQuery_v3")
        json_data = {
            "parameters": [
                {"paramCode": "prisoner_id", "value": criminalId},
                {"paramCode": "assessment_id", "value": assessment_id}
            ]
        }
        try:
            res = self.police_client.post(url, json=json_data)
            return res.json()
        except Exception as e:
            self.logger.error(f'police_search_zfz_factory 请求出错: {e}')
            return None

    @police_login()
    def police_close_package_all(self, criminalId=None):
        """
        关闭罪犯所有业务包
        :param criminalId:
        :return:
        """
        criminalId = criminalId or self.users['criminal']['id']
        ids = []

        res = self.police_process_record_search(criminalId=criminalId, retry=False)[
            'resultList']
        if not res:
            self.logger.debug(f'{criminalId} 没有正在进行中任务')
            return None
        for task in res:
            ids.append(task['id'])
        cancelReason = '自动化关闭'
        url = self._build_url("/comprehensive-assessment-system/crime-Business/v1.0/package/instance/packageClose")
        for item_id in ids:
            self.police_client.get(url=url,
                                   params={'cancelReason': cancelReason, 'packageInstanceId': item_id})
        time.sleep(1)
        return StepStatus.PASS

    @police_login()
    def police_close_package(self, criminalId=None, assessment: Assessment = None):
        """
        关闭指定业务包
        :param criminalId:
        :param assessment:
        :return:
        """
        # 使用更规范的变量名，明确默认值来源
        criminal_id = criminalId or self.users['criminal']['id']
        try:
            # 获取流程记录，明确不重试
            process_records = self.police_process_record_search(
                criminalId=criminal_id,
                assessment=assessment,
                retry=False
            )
            if not process_records['resultList']:
                self.logger.debug(f"罪犯 {criminal_id} 没有正在进行中的任务")
                return
            # 提取ID列表（使用列表推导式更简洁）
            package_ids = [task['id'] for task in process_records['resultList']]
            self.logger.debug(f"准备关闭罪犯 {criminal_id} 的业务包，ID列表: {package_ids}")

            # 构建URL（只构建一次）
            url = self._build_url(
                "/comprehensive-assessment-system/crime-business/v1.0/package/instance/packageClose"
            )

            # 关闭所有业务包
            cancel_reason = '自动化关闭'
            for pkg_id in package_ids:
                response = self.police_client.get(
                    url=url,
                    params={'cancelReason': cancel_reason, 'packageInstanceId': pkg_id}
                )
                if response.status_code == 200:
                    self.logger.debug(f"已关闭业务包 {pkg_id}")
                else:
                    self.logger.error(f"关闭业务包 {pkg_id} 失败，状态码: {response.status_code}")
                    raise

        except Exception as e:
            self.logger.error(f"关闭业务包时发生错误: {str(e)}", exc_info=True)
            # 可以根据需要决定是否重新抛出异常

    @police_login()
    def police_batch_start(self, criminalId='', assessment: Assessment = Assessment,
                           trigger_mode='手动触发', easy_flow='否'):
        """
        :param criminalId:
        :param assessment: Assessment 枚举类 评估
        :param trigger_mode: 处罚方式  默认手动处罚
        :param easy_flow: 默认一般  否
        :return:
        """
        self.logger.debug(f'police_batch_start 执行 发起评估{assessment}')
        url = self._build_url("/comprehensive-assessment-system/crime-business/v1.0/instance/batchStart")
        json_data = [
            {
                "flowIds": assessment.value['flowIds'],
                "criminalId": criminalId or self.users['criminal']['id'],
                "packageCode": assessment.value['packageCode'],
                "triggerMode": trigger_mode,
                "easyFlow": easy_flow
            }
        ]
        self.logger.debug(f'请求体{json_data}')
        try:
            res = self.police_client.post(url, json=json_data).json()
            if res['code'] != "200" :
                raise AssertionError(f'发起评估失败 {res["msg"]}')
            elif  not res['content'][0]['successData']:
                raise AssertionError(f'发起评估失败 流程未打开{res["msg"]}')
            time.sleep(3)
            self.current_process_information['initiate_process_res'] = res['content'][0]['successData'][0]
            return res
        except Exception as e:
            self.logger.error(f'police_batch_start 请求出错: {e}')
            raise AssertionError(f'发起评估失败  {e}')

    def update_current_process_information(self):
        self.current_process_information = self.police_assessment_process_search()['resultList'][0]
        return self.current_process_information

    @police_login()
    def police_search_criminal_basic_information(self, criminalId='', policeId=""):
        """
        搜索罪犯
        :param criminalId:
        :param policeId:
        :return:
        """

        self.logger.debug(f'罪犯基本信息')
        url = self._build_url("/comprehensive-assessment-system/ficus/v1/viewPortQuery/S1/deyang/queryOverview")
        params = {
            "parameters": [
                {
                    "paramCode": "id",
                    "value": criminalId or self.users['criminal']['id']
                }
            ]
        }

        try:
            res = self.police_client.post(url, json=params)
            res.raise_for_status()  # 触发HTTP错误（如400/500）
            self.criminal_information = res.json()['resultList'][0]
            return self.criminal_information
        except Exception as e:
            # 仅记录业务错误，登录相关错误由装饰器处理
            self.logger.error(f'搜索罪犯信息失败（业务错误）：{e}')
            raise f'搜索罪犯信息失败（业务错误）：{e}'

    @police_login()
    def police_check_submit(self, criminalId='', policeId=""):
        id = generate_random_number()
        url = self._build_url("/app-factory-web/app-factory/v1.0/sheet/submit/check/")
        try:
            res = self.police_client.get(url + str(id))
        except Exception as e:
            self.logger.error(f'police_check_submit 请求出错: {e}')
            return None

    @police_login()
    def police_package_list(self, **kwargs):
        """
        查询流程 列表
        :param kwargs:
        :return:
        """
        params = {'codeOrName': kwargs.get('criminalId', self.users['criminal']['id']),
                  'status': kwargs.get('status', ['RUNNING', 'RUNNING']),
                  'folderCode': kwargs.get('folderCode', '')
                  }
        url = self._build_url("/comprehensive-assessment-system/crime-Business/v1.0/package/instance/packageList")
        self.package_list = self.police_client.get(url, params=params).json()['resultList']
        return self.package_list

    @global_retry()
    def get_afpTaskId(self, stepCode: ProcessNode) -> str:
        """
        获取指定流程步骤的afpTaskId
        :param stepCode:
        :return:
        """
        # 获取ID
        package_list = self.police_package_list()
        if not package_list:
            self.logger.error("未获取到流程列表")
            raise AssertionError("未获取到流程列表")

        package_id = package_list[0]['id']

        # 获取任务记录
        task_res = self.police_process_node_information(packageId=package_id, stepCode=stepCode)

        # 验证响应结构
        content = task_res.get('content')
        if not content or not isinstance(content, list) or len(content) == 0:
            self.logger.error(f"任务记录响应格式异常: {task_res}")
            raise AssertionError("任务记录内容为空")

        flow_tasks = content[0].get('flowTaskPO')
        if not flow_tasks or not isinstance(flow_tasks, list):
            self.logger.error(f"flowTaskPO格式异常: {flow_tasks}")
            raise AssertionError("任务流程列表为空")

        # 查找匹配的任务ID
        matching_tasks = [task for task in flow_tasks if task.get('stepCode') == stepCode.value]

        if not matching_tasks:
            self.logger.error(f"未找到stepCode={stepCode.value}的任务")
            raise AssertionError(f"未找到匹配步骤的任务: {stepCode.name}")

        return matching_tasks[0]['afpTaskId']

    @police_login()
    def police_sheet_submit(self, **kwargs):
        """
        查询待办事项
        :param kwargs:
        :return:
        """
        # 获取节点信息
        data = kwargs.get('data')
        url = self._build_url("/app-factory-web/app-factory/v1.0/sheet/submit/")
        res = self.police_client.post(url + self.current_process_information['afpTaskId'], json=data)
        if res.status_code != 200:
            raise AssertionError('更新表单失败')

    ## 流程记录
    @global_retry()
    @police_login()
    def police_get_current_process_information(self, processNode: ProcessNode):
        """
        获取当前进行中的流程信息

        :param processNode: 流程节点对象
        :return: 流程信息数据，获取失败时返回None
        """
        try:
            self.logger.info(f'获取当前进行中的流程信息: {processNode}')

            # 减少深层字典访问，提高可读性
            initiate_process_res = self.current_process_information.get('initiate_process_res', {})
            package_instance_id = initiate_process_res.get('packageInstanceId')

            if not package_instance_id:
                self.logger.error("未能获取到packageInstanceId")
                return None

            process_list = self.police_process_node_information(package_instance_id)

            # 提取流程任务信息
            target_task = None
            for process in process_list:
                flow_tasks = process.get('flowTaskPO', [])
                for task in flow_tasks:
                    if task.get('flowProcessStepName') == processNode.name:
                        target_task = task
                        break  # 找到目标任务，退出内层循环
                if target_task:
                    break  # 找到目标任务，退出外层循环

            if not target_task:
                self.logger.error(f"未找到名称为{processNode.name}的流程任务")
                return None

            # 更新当前流程信息
            self.current_process_information['afpTaskId'] = target_task['afpTaskId']
            self.current_process_information['flowInstanceId'] = target_task['flowInstanceId']
            self.current_process_information['status'] = target_task['status']

            # 获取并返回表单任务数据
            return self.police_sheet_task(afpTaskId=self.current_process_information['afpTaskId'])

        except KeyError as e:
            self.logger.error(f'获取当前进行中的流程信息时缺少必要键: {e}，重试')
            raise  # 重新抛出异常，触发重试机制
        except Exception as e:
            self.logger.error(f'获取当前进行中的流程信息失败: {e}，重试')
            raise  # 重新抛出异常，触发重试机制

    ## 流程记录查询  小包
    @global_retry()
    @police_login()
    def police_process_record_search(self, assessment: Assessment = None, status=None, criminalId: str = None,
                                      retry=True):
        """
        流程记录 查询
        :param retry: 重试
        :param assessment: 评估，通过评估 folderCode 筛选业务包  查询子包，不查询大包
        :param status: 运行状态  默认审核中和进行中
        :param criminalId: 罪犯ID
        :return:
        """
        # 日志记录评估信息
        if assessment:
            self.logger.debug(f'查询评估: {assessment.name}')
        # 参数处理与默认值设置
        folder_code = assessment.value['packageCode'] if assessment else ''
        status = status or ['RUNNING', 'AUDIT']
        criminal_id = criminalId or self.users['criminal']['id']

        # 构建请求URL
        url = self._build_url("/comprehensive-assessment-system/crime-business/v1.0/package/instance/packageList")

        try:
            # 发送请求
            response = self.police_client.get(
                url=url,
                params={
                    'codeOrName': criminal_id,
                    "status": status,
                    'folderCode': folder_code
                }
            )

            # 检查响应是否有效
            if not response :
                self.logger.error('查询流程记录失败：未获取到响应')
                raise AssertionError('查询流程记录失败：未获取到响应')

            # 解析JSON响应
            result = response.json()

            # 处理不重试场景
            if not retry:
                return result

            # 记录空结果信息
            if not result.get('resultList'):
                self.logger.debug(
                    f"罪犯 {criminal_id} 未查询到状态为 {status} 的进行中流程记录"
                )
                return False

            return result

        except json.JSONDecodeError:
            self.logger.error('查询流程记录失败：响应内容不是有效的JSON格式')
            raise
        except Exception as e:
            self.logger.error(f'查询流程记录失败：{str(e)}', exc_info=True)
            raise

    # 子包查询
    @global_retry()
    @police_login()
    def police_process_node_information(self, id=None):
        """
        任务流程信息  通过package
        :param id:
        :return:
        """
        try:
            self.logger.info(f'查询子包信息，packageInstanceId: {id}')
            url = self._build_url("/comprehensive-assessment-system/crime-business/v1.0/instance/instanceAndTask/")
            node_information = self.police_client.get(url + id)

            package_list = node_information.json()['content']
            if not package_list:
                self.logger.debug(f"<UNK> {id} <UNK>")
            return package_list
        except Exception as e:
            self.logger.error(e)

    @global_retry()
    @police_login()
    def police_sheet_task(self, afpTaskId: str):
        """
        sheet task
        :param afpTaskId:
        :return:
        """

        params = {'fixVirtualField': True}
        url = self._build_url("/app-factory-web/app-factory/v1.0/sheet/task/")
        try:
            res = self.police_client.get(url + afpTaskId, params)
            return res.json()
        except Exception as e:
            self.logger.error(f"重试查询 sheet task")
            raise  # 抛出异常以触发重试

    @police_login()
    def police_report_source_id(self, id):
        """
        报告id
        :param id:
        :return:
        """
        url = self._build_url("/comprehensive-assessment-system/crime-Business/v1.0/audit/" + id + '/contents')
        try:
            res = self.police_client.get(url)
            return res.json()
        except Exception as e:
            self.logger.error('获取报告content失败')

    @police_login()
    def police_report_result(self, id):
        """
        报告内容
        :param id: sourceId
        :return:
        """
        url = self._build_url("/comprehensive-assessment-system/crime-Business/v1.0/reportResult/")
        res = self.police_client.get(url + id)
        self.current_process_information['reportResult'] = res.json()['content']
        self.police_audit_report_detail(self.current_process_information['reportResult']['tblReportId'])
        return res.json()

    @police_login()
    def police_leader_audit_pass(self, process: Process = Process):
        """
        监区领导审核
        :param process:
        :return:
        """
        # 查询审核列表
        auditList = self.police_audit_search()['resultList']
        processId = ''
        sourceId = ''
        reportContent = {}
        # 获取流程ID
        if auditList is not None:
            for audit in auditList:
                if process.value == audit['processId']:
                    processId = audit['id']
                    # 获取报告id
                    sourceId = self.police_report_source_id(id=processId)['sourceId']
                    # 获取报告内容
                    reportContent = self.police_report_result(id=sourceId)['content']
        if processId == '':
            self.logger.error('未找到流程对应审核')
            raise AssertionError('未找到流程对应审核')
        return processId, sourceId, reportContent

    # 待办事项
    @global_retry()
    @police_login()
    def police_assessment_process_search(self, criminalId=''):
        """
        待办事项 评估流程查询
        :param criminalId:
        :return:
        """
        criminalId = criminalId or self.users['criminal']['id']
        self.logger.debug(f'{self.users[self.current_user.name]['username']} 查询 {criminalId} 待办')
        url = self._build_url("/comprehensive-assessment-system/crime-Business/v1.0/task/queryV2")
        params = {
            "focus": False,
            "keyword": criminalId,
            "needCount": True,
            "page": "1",
            "scope": "WEB",
            "size": "10",
            "type": "TASK"
        }
        res = self.police_client.get(url, params).json()
        if res['resultList'] is None:
            self.logger.error('待办事项为空,正在重试')
            raise ValueError("待办事项为空")
        # self.current_process_information['task'] = res['resultList']
        return res

    # 查询流程
    @global_retry()
    @police_login()
    def police_process_status(self, flowInstanceId):
        """
        流程状态
        :param flowInstanceId:
        :return:
        """
        url = self._build_url("/comprehensive-assessment-system/crime-Business/v1.0/instance/")
        res = self.police_client.get(url + flowInstanceId + '/status')

        return res

    # 个体危险信息
    @police_login()
    def police_gtwx_information(self, flowInstanceId):
        """
        个体危险信息
        :param flowInstanceId:
        :return:
        """
        url = self._build_url("/comprehensive-assessment-system/ficus/v1/viewPortQuery/S1/deyang/gtwxActObs")
        data = {
            "parameters": [
                {
                    "paramCode": "bh",
                    "value": self.users['criminal']['id']
                },
                {
                    "paramCode": "flowInstanceId",
                    "value": flowInstanceId
                }
            ]
        }
        res = self.police_client.post(url, json=data)
        return res

    # 档卡基本信息-犯罪情况
    @police_login()
    def police_dk_information(self, flowInstanceId):
        """
        个体危险信息
        :param flowInstanceId:
        :return:
        """
        url = self._build_url("/comprehensive-assessment-system/ficus/v1/viewPortQuery/S1/deyang/dkdajbxx")
        data = {
            "parameters": [
                {
                    "paramCode": "id",
                    "value": self.users['criminal']['id']
                },
                {
                    "paramCode": "flowInstanceId",
                    "value": flowInstanceId
                }
            ]
        }
        res = self.police_client.post(url, json=data)
        return res

    # 审核事件查询
    def police_audit_data(self, user_type: HUIXIN_USER):
        auditProcess = self.police_audit_search(user_type=user_type)['resultList'][0]

        sourId = self.police_report_source_id(id=auditProcess['id'])[0]['sourceId']
        res = self.police_report_result(id=sourId)
        self.current_process_information['reportResult']['audit_id'] = auditProcess['id']
        return self.current_process_information

    @global_retry()
    @police_login()
    def police_audit_search(self, criminalId=None):
        """
        审核列表
        :param criminalId:
        :return:
        """
        criminalId = criminalId or self.users['criminal']['id']
        params = {'focus': False, 'isFilterPolicy': True, 'page': 1, 'pageSize': 100, 'status': 'NEW', 'type': 'AUDIT',
                  'keyword': criminalId}
        url = self._build_url("/comprehensive-assessment-system/crime-business/v1.0/audit")
        res = self.police_client.get(url, params)
        if len(res.json()['resultList']) == 0:
            self.logger.error(
                f'警察：{self.users[self.current_user.name]['username']}：无待审核{criminalId}  正在重试....')
            raise ValueError
        self.current_process_information['reportResult'] = res.json()
        return res.json()

    # 报告内容
    @police_login()
    def police_audit_report_content(self, id):
        """
        审核列表
        :param id:
        :return:
        """
        url = self._build_url("/comprehensive-assessment-system/crime-Business/v1.0/audit/")
        res = self.police_client.get(url + id + '/contents')
        return res.json()

    # 报告内容详情
    @police_login()
    def police_audit_report_detail(self, tblReportId):
        """
        审核列表
        :param tblReportId:
        :return:
        """
        url = self._build_url("/comprehensive-assessment-system/crime-Business/v1.0/report/detail/")
        res = self.police_client.get(url + tblReportId)
        self.current_process_information['report_detail'] = res.json()['content']
        return res.json()

    # 待办事项-审核
    @police_login()
    def police_audit_submit(self, data, save=True):
        """
        提交审核
        :data : 审核参数构造  audit_gtwx_leader_police
        :return:
        """

        audit_data = data.get('audit_data', data)
        id = data.pop('id')
        history_data = data.get('history_data', '')
        remark = ''
        if 'remark' in data:
            remark = data.pop('remark')
            url = self._build_url(
                f"/comprehensive-assessment-system/crime-Business/v1.0/audit/submit/{id}?status=PASS&remark={remark}")

        url = self._build_url(
            f"/comprehensive-assessment-system/crime-Business/v1.0/audit/submit/{id}?status=PASS")
        res = self.police_client.post(url, json=audit_data)
        if res.status_code == 200 and history_data:
            self.police_audit_save_history(history_data)
        else:
            self.logger.error('审核失败')
            raise AssertionError('审核失败')
        return res

    @police_login()
    def police_audit_save_history(self, data):
        """
        存储审核
        :param data:
        :return:
        """
        url = self._build_url("/comprehensive-assessment-system/onlyoffice/saveHistory")
        # json = {
        #     'hObjectNameList': [
        #         {
        #             "afpInstanceId": data['afpInstanceId'],
        #             'assessmentFlowInstanceId': data['assessmentFlowInstanceId'],
        #             "templateObjectName": data["templateObjectName"],
        #             "hObjectName": data['hObjectName'],
        #             "pObjectName": data['pObjectName'],
        #             "reportResultId": data['reportResultId'],
        #             "reportId": data['reportId'],
        #             "reportName": data['reportName'],
        #             "fileData": data['fileData'],
        #             "fieldsPrivilege": data['fieldsPrivilege']
        #         }
        #     ],
        #     'stepName': self.current_user.value,
        # }
        res = self.police_client.post(url, json=data)
        if res.status_code != 200:
            self.logger.error('police_audit_save_history执行失败')
            raise ValueError
        self.logger.debug('police_audit_save_history执行成功')


if __name__ == "__main__":
    p = PoliceSystem()

    # p.police_init_body_heart_table()
    # p.police_search_criminal_basic_information()
    # res = p.police_process_record_task(packageId='1920379313836781570')
    # p.police_sheet_task(taskId='840620890247950336')
    # p.police_process_status(id='adb164d38f534ba982d42cf1035312fa')
    # p.police_assessment_process_search()
    # p.police_search_criminal_basic_information()
    # p.police_process_record_search()
    p.police_get_current_process_information(
        assessment=Assessment.入监_罪犯基本信息采集,
        processNode=ProcessNode.身心健康_辅助检查详细指标)
    # p.police_get_current_process_information(user_type=HUIXIN_USER.doctor_police)
