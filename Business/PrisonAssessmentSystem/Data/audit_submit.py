import json
import time
from datetime import datetime

from Business.PrisonAssessmentSystem.Data import Process, HUIXIN_USER
from Business.PrisonAssessmentSystem.Service.HuiXinService import HuiXinService


class AuditSubmitDataFactory:
    """<UNK>"""

    def __init__(self, huiXinService: HuiXinService):
        self.huixin_server = huiXinService
        self.audit_user = {}

    def create_inmate_criminal_base_info(self, process: Process, user_type: HUIXIN_USER):
        def data_generator():
            try:
                self.huixin_server.current_user = user_type
                data = self.huixin_server.police_get_audit_info(process)
                return {
                    'auditId': data.get('auditId'),
                    'remark': '自动化-通过',
                    'auditData': {
                        "reportFileData": []
                    }
                }
            except Exception as e:
                raise

        return data_generator

    def create_inmate_gtwx_audit_data(self, process: Process, user_type: HUIXIN_USER, **kwargs):
        def data_generator():
            try:
                self.huixin_server.current_user = user_type
                self.audit_user[self.huixin_server.users[self.huixin_server.current_user.name]['role']] = {
                    "auditor": self.huixin_server.users[self.huixin_server.current_user.name]['name'],
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

                data = self.huixin_server.police_get_audit_info(process)

                fileData = fileData = {
                    "reason": '',
                    "measure": '',
                    "review_violent": [
                        kwargs.get('violent_tendency', "低")
                    ],
                    "review_break": [
                        kwargs.get('escape_tendency', "低")
                    ],
                    "review_suicide": [
                        kwargs.get('suicide_tendency', "低")
                    ],
                    "review_danger_level": [
                        kwargs.get('danger_level', "低")
                    ],
                    "policeopinion": "",
                    "prisonopinion": "",
                    "assessmentcentreopinion": "",
                    "__auditInfo": {}
                }
                fileData.update(json.loads(data['reportResult']['executeResult']))
                fileData['__auditInfo'] = self.audit_user
                fileData['policeopinion'] = "自动化测试-民警" if '主管民警' in self.audit_user else ""
                fileData['prisonopinion'] = "自动化测试-监区领导" if '监区领导' in self.audit_user else ""
                fileData['assessmentcentreopinion'] = "自动化测试-评估中心" if '评估中心' in self.audit_user else ""

                fileObjectName = f"history/{data['reportResult']['afpInstanceId']}/@个体危险评估【报告】@{int(time.time() * 1000)}.docx"
                return {
                    'auditId': data.get('auditId'),
                    'remark': '自动化-通过',
                    'auditData': {
                        "reportFileData": [
                            {
                                "afpInstanceId": data['reportResult']['afpInstanceId'],
                                "reportId": data['reportResult']['tblReportId'],
                                "fileObjectName": fileObjectName,
                                "fileData": fileData,
                                "assessmentFlowInstanceId": data['reportContent'][0]['flowInstanceId'],
                            }
                        ]
                    },
                    'saveData': {
                        "hObjectNameList": [
                            {
                                "afpInstanceId": data['reportResult']['afpInstanceId'],
                                "templateObjectName": "template/34tUTJg1J8.docx",
                                "hObjectName": fileObjectName,
                                "pObjectName": data['reportResult']['fileName']['objPath'],
                                "reportResultId": data['reportResult']['id'],
                                "reportId": data['reportResult']['tblReportId'],
                                "reportName": "个体危险评估【报告】",
                                "assessmentFlowInstanceId": data['reportContent'][0]['flowInstanceId'],
                                "fileData": fileData,
                                "fieldsPrivilege": data['reportContent'][0]['flowInstanceId']
                            }
                        ],
                        "stepName": self.huixin_server.users[self.huixin_server.current_user.name]['role'],
                    }
                }
            except Exception as e:
                raise

        return data_generator

    def create_middle_gtwx_audit_data(self, process: Process, user_type: HUIXIN_USER, **kwargs):
        """创建中期-个体危险审核数据"""

        def data_generator():
            try:
                self.huixin_server.current_user = user_type
                self.audit_user[self.huixin_server.users[self.huixin_server.current_user.name]['role']] = {
                    "auditor": self.huixin_server.users[self.huixin_server.current_user.name]['name'],
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                res = self.huixin_server.police_audit_init(process=process)
                auditId = res['resultList'][0]['id']
                reportContent = self.huixin_server.service.police_reportContent(auditId=auditId)
                assert reportContent.status_code == 200, f'{self.huixin_server.current_user}查询报告内容 {auditId} 失败：{reportContent.text} 重试'
                reportId = reportContent.json()[0]['sourceId']
                fieldsPrivilege = reportContent.json()[0]['fieldsPrivilege']
                reportResult = self.huixin_server.service.police_reportResult(reportId=reportId)
                assert reportResult.status_code == 200, f'{self.huixin_server.current_user}查询报告结果 {reportId} 失败：{reportResult.text} 重试'
                report = reportResult.json()['content']
                objPath = report['fileName']['objPath']
                reportName = report['fileName']['fileName']
                execute = json.loads(report['executeResult'])
                # """创建中期-个体危险审核数据"""
                fileName = f"history/{report['afpInstanceId']}/@个体危险评估【报告】@{int(time.time() * 1000)}.docx"
                fileData = {
                    "reason": '',
                    "measure": '',
                    "review_violent": [
                        kwargs.get('violent_tendency', "低")
                    ],
                    "review_break": [
                        kwargs.get('escape_tendency', "低")
                    ],
                    "review_suicide": [
                        kwargs.get('suicide_tendency', "低")
                    ],
                    "review_danger_level": [
                        kwargs.get('danger_level', "低")
                    ],
                    "policeopinion": "",
                    "prisonopinion": "",
                    "assessmentcentreopinion": "",
                    "__auditInfo": {}
                }
                fileData.update(execute)
                fileData['__auditInfo'] = self.audit_user
                fileData['policeopinion'] = "自动化测试-民警" if '主管民警' in self.audit_user else ""
                fileData['prisonopinion'] = "自动化测试-监区领导" if '监区领导' in self.audit_user else ""
                fileData['assessmentcentreopinion'] = "自动化测试-评估中心" if '评估中心' in self.audit_user else ""
                data = {
                    'auditId': auditId,
                    "auditData": {
                        "reportFileData": [
                            {
                                "afpInstanceId": report['afpInstanceId'],
                                "reportId": report['tblReportId'],
                                "fileObjectName": fileName,
                                "fileData": fileData,
                                "assessmentFlowInstanceId": report['flowInstanceId'],
                            }
                        ]
                    },
                    "saveData": {
                        "hObjectNameList": [
                            {
                                "afpInstanceId": report['afpInstanceId'],
                                "templateObjectName": "template/34tUTJg1J8.docx",
                                "hObjectName": fileName,
                                "pObjectName": objPath,
                                "reportResultId": report['id'],
                                "reportId": report['tblReportId'],
                                "reportName": reportName,
                                "assessmentFlowInstanceId": report['flowInstanceId'],
                                "fileData": fileData,
                                "fieldsPrivilege": fieldsPrivilege
                            }
                        ],
                        "stepName": self.huixin_server.users[self.huixin_server.current_user.name]['role'],
                    }
                }
                return data
            except Exception as e:
                self.huixin_server.logger.error(e)
                raise e

        return data_generator

    def create_out_zfz_audit_data(self, process: Process, user_type: HUIXIN_USER, **kwargs):
        """创建出监-再犯罪审核数据"""

        def data_generator():
            try:
                self.huixin_server.current_user = user_type
                self.audit_user[self.huixin_server.users[self.huixin_server.current_user.name]['role']] = {
                    "auditor": self.huixin_server.users[self.huixin_server.current_user.name]['name'],
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                criminal_info = self.huixin_server.criminal_information['baseinfo']
                res = self.huixin_server.police_audit_init(process=process)
                auditId = res['resultList'][0]['id']
                reportContent = self.huixin_server.service.police_reportContent(auditId=auditId)
                assert reportContent.status_code == 200, f'{self.huixin_server.current_user}查询报告内容 {auditId} 失败：{reportContent.text} 重试'
                reportId = reportContent.json()[0]['sourceId']
                fieldsPrivilege = reportContent.json()[0]['fieldsPrivilege']
                reportResult = self.huixin_server.service.police_reportResult(reportId=reportId)
                assert reportResult.status_code == 200, f'{self.huixin_server.current_user}查询报告结果 {reportId} 失败：{reportResult.text} 重试'
                report = reportResult.json()['content']
                objPath = report['fileName']['objPath']
                reportName = report['fileName']['fileName']
                execute = json.loads(report['executeResult'])
                # """创建中期-个体危险审核数据"""
                fileName = f"history/{report['afpInstanceId']}/@再犯罪评估【报告】@{int(time.time() * 1000)}.docx"
                fileData = {
                    "__extend": {
                        "easyFlow": "否"
                    },
                    'crimelg': '否',
                    "isVeryHigh": True,
                    "recordInfo": [],
                    "isCustomFlow": True,
                    "isSimpleFlow": False,
                    "reviewresults": '',
                    "isExecOutPrison": False,
                    "review_zfzlevel": [
                        "一般"
                    ],
                    "reason": '',
                    "measure": '',
                    "__auditInfo": {}
                }
                fileData.update(execute)
                fileData['__auditInfo'] = self.audit_user
                fileData['policeopinion'] = "自动化测试-民警" if '主管民警' in self.audit_user else ""
                fileData['prisonopinion'] = "自动化测试-监区领导" if '监区领导' in self.audit_user else ""
                fileData['assessmentcentreopinion'] = "自动化测试-评估中心" if '评估中心' in self.audit_user else ""
                fileData['review_zfzlevel'] = ["一般"]
                data = {
                    'auditId': auditId,
                    "auditData": {
                        "reportFileData": [
                            {
                                "afpInstanceId": report['afpInstanceId'],
                                "reportId": report['tblReportId'],
                                "fileObjectName": fileName,
                                "fileData": fileData,
                                "assessmentFlowInstanceId": report['flowInstanceId'],

                            }
                        ]
                    },
                    "saveData": {
                        "hObjectNameList": [
                            {
                                "afpInstanceId": report['afpInstanceId'],
                                "templateObjectName": "pre/ASmOojehH.docx",
                                "hObjectName": fileName,
                                "pObjectName": objPath,
                                "reportResultId": report['id'],
                                "reportId": report['tblReportId'],
                                "reportName": reportName,
                                "assessmentFlowInstanceId": report['flowInstanceId'],
                                "fileData": fileData,
                                "fieldsPrivilege": fieldsPrivilege
                            }
                        ],
                        "stepName": self.huixin_server.users[self.huixin_server.current_user.name]['role'],
                    }
                }
                return data
            except Exception as e:
                self.huixin_server.logger.error(e)
                raise e

        return data_generator
