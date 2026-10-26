from Business.PrisonAssessmentSystem.BaseCases.CriminalBase import CriminalBase
from Business.PrisonAssessmentSystem.Data import ProcessNode, Assessment, ProcessStepStatus, HUIXIN_USER, Process
from Business.PrisonAssessmentSystem.Data.audit_submit import AuditSubmitDataFactory
from Business.PrisonAssessmentSystem.Data.in_prison import In_DataFactory
from Business.PrisonAssessmentSystem.Data.sheet_submit import SheetSubmitDataFactory
from TestRunner.core.Base import StepStatus

case_name = '创建报告'


class create_report(CriminalBase):
    def setUp(self):
        pass

    def defineSteps(self):
        # 环境清理，关闭业务包
        self.def_step(step_name="复制报告",
                      method=self.create_new_report, )

    def create_new_report(self):
        """
        复制报告
        :return:
        """
        data = self.get_report_data()
        res = self.huixin_server.service.app_update_report(data)
        assert res.status_code == 200, f"复制报告失败：{res.text}"


    def get_report_data(self):
        """
        获取报告数据
        :return:
        """
        reportId = self.params['report_id']
        reportName = self.params['report_name']
        #
        # newReportId = ''
        # newReportName = f'{reportName}【报告】【复制】'
        #
        # config = self.huixin_server.service.app_config()
        # assert config.status_code == 200, "获取配置失败"
        # config = config.json()
        #
        reportDetail = self.huixin_server.service.app_report_detail(reportId)
        assert reportDetail.status_code == 200, f"获取报告详情失败：{reportId}"
        reportDetail = reportDetail.json()

        reportStyle = self.huixin_server.service.app_report_style(reportId)
        assert reportStyle.status_code == 200, f"获取报告样式失败：{reportId}"
        reportStyle = reportStyle.json()

        reportList = self.huixin_server.service.app_report_list()
        assert reportList.status_code == 200, "获取报告列表失败"
        reportList = reportList.json()['resultList']

        match reportName:
            case '认罪悔改评估':
                newReportId = '1930094459273900034'
                return {
                    "id": "1930094459273900034",
                    "formId": "850325312460845056",
                    "processId": "850325313027076096",
                    "fileName": "template/EaMskWBuEJ.docx",
                    "name": "认罪悔改评估【报告】【复制】",
                    "remark": '复制',
                    'reportStyleVOList': [
                        {
                            "id": "1824000468512677889",
                            "solutionCode": "deyang",
                            "name": "getFlowPeriod",
                            "viewport": "getFlowPeriodFromFlowInstanceId",
                            "type": 0,
                            "script": '',
                            "reportId": "474622176897192348",
                            "viewportParams": [
                                {
                                    "key": "0",
                                    "name": "flowInstanceId",
                                    "type": "dynamic",
                                    "value": "flowInstanceId"
                                }
                            ],
                            "dataAnalysis": ''
                        },
                        {
                            "id": "1824000468512677890",
                            "solutionCode": "deyang",
                            "name": "isCustomFlow",
                            "viewport": '',
                            "type": 3,
                            "script": "getFlowPeriod[0].type === '正常流程'",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "1824000468512677891",
                            "solutionCode": "deyang",
                            "name": "isSimpleFlow",
                            "viewport": '',
                            "type": 3,
                            "script": "getFlowPeriod[0].type === '简易流程'",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "1824003765575360514",
                            "solutionCode": "deyang",
                            "name": "period",
                            "viewport": '',
                            "type": 3,
                            "script": "getFlowPeriod[0].period",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "1828329047748644866",
                            "solutionCode": "deyang",
                            "name": "review_rzhglevel",
                            "viewport": '',
                            "type": 3,
                            "script": '',
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b89ee1c6-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "id",
                            "viewport": '',
                            "type": 3,
                            "script": "overview[0].baseinfo.id",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b89f3b02-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "name",
                            "viewport": '',
                            "type": 3,
                            "script": "overview[0].baseinfo.name",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b89f66fc-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "preson_area",
                            "viewport": '',
                            "type": 3,
                            "script": "overview[0].baseinfo.preson_area",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b89f9337-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "birthday",
                            "viewport": '',
                            "type": 3,
                            "script": "overview[0].baseinfo.birthday",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b89fbfbb-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "sex",
                            "viewport": '',
                            "type": 3,
                            "script": "overview[0].baseinfo.sex",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b89fec38-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "marriage_now",
                            "viewport": '',
                            "type": 3,
                            "script": "overview[0].baseinfo.marriage_now",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a01929-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "nation",
                            "viewport": '',
                            "type": 3,
                            "script": "overview[0].baseinfo.nation",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a04521-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "native_place",
                            "viewport": '',
                            "type": 3,
                            "script": "overview[0].baseinfo.native_place",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a070a9-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "education",
                            "viewport": '',
                            "type": 3,
                            "script": "overview[0].baseinfo.education",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a09d57-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "family_address",
                            "viewport": '',
                            "type": 3,
                            "script": "overview[0].baseinfo.family_address",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a0ca3d-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "crimelg",
                            "viewport": '',
                            "type": 3,
                            "script": "overview[0].baseinfo.$CrimeLg",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a0f679-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "wushe",
                            "viewport": '',
                            "type": 3,
                            "script": "overview[0].baseinfo.$WuShe",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a12361-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "crime_record_count",
                            "viewport": '',
                            "type": 3,
                            "script": "overview[0].baseinfo.$crime_record_count",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a14fa6-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "crime_name",
                            "viewport": '',
                            "type": 3,
                            "script": "overview[0].baseinfo.crime_name",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a17cf5-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "xq",
                            "viewport": '',
                            "type": 3,
                            "script": "overview[0].baseinfo.xq",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a1a941-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "enter_data",
                            "viewport": '',
                            "type": 3,
                            "script": "overview[0].baseinfo.enter_data",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a1d5ed-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "dqxxqr",
                            "viewport": '',
                            "type": 3,
                            "script": "overview[0].baseinfo.DQXQQR",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a20247-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "penaldetail",
                            "viewport": '',
                            "type": 3,
                            "script": "overview[0].baseinfo.penalDetail",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a22e3b-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "yx",
                            "viewport": '',
                            "type": 3,
                            "script": "overview[0].baseinfo.yx",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a25abf-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "dqxqzr",
                            "viewport": '',
                            "type": 3,
                            "script": "overview[0].baseinfo.DQXQZR",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a286f4-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "conclusion_beginTime",
                            "viewport": '',
                            "type": 3,
                            "script": "assessment[0].beginTime",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a2b41b-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "rztd",
                            "viewport": '',
                            "type": 3,
                            "script": "apply[0].rztd",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a2dfd2-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "explain",
                            "viewport": '',
                            "type": 3,
                            "script": "assessment[0].explain",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a30c47-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "suggest",
                            "viewport": '',
                            "type": 3,
                            "script": "assessment[0].suggest",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a33914-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "assessment_time",
                            "viewport": '',
                            "type": 3,
                            "script": "assessment[0].assessment_time",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a36500-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "rzhg_score",
                            "viewport": '',
                            "type": 3,
                            "script": "assessment[0].sum_score",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a391a3-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "assessment_tab_obj",
                            "viewport": '',
                            "type": 3,
                            "script": "assessment[0].assessment_tab_obj",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a3be71-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "conclusion_endTime",
                            "viewport": '',
                            "type": 3,
                            "script": "assessment[0].endTime",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a3eb5b-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "rzhg_result",
                            "viewport": '',
                            "type": 3,
                            "script": "assessment[0].text_result",
                            "reportId": "474622176897192348",
                            "viewportParams": '',
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a4177d-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "overview",
                            "viewport": "queryOverview",
                            "type": 0,
                            "script": '',
                            "reportId": "474622176897192348",
                            "viewportParams": [
                                {
                                    "key": "0",
                                    "name": "id",
                                    "type": "dynamic",
                                    "value": "criminalId"
                                }
                            ],
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a44454-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "assessment",
                            "viewport": "Fb2AssessmentReportQuery",
                            "type": 0,
                            "script": '',
                            "reportId": "474622176897192348",
                            "viewportParams": [
                                {
                                    "key": "0",
                                    "name": "criminalId",
                                    "type": "dynamic",
                                    "value": "criminalId"
                                },
                                {
                                    "key": "1",
                                    "name": "flowInstanceId",
                                    "type": "dynamic",
                                    "value": "flowInstanceId"
                                }
                            ],
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a4704d-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "apply",
                            "viewport": "rzhzReporIsAppealQuery",
                            "type": 0,
                            "script": '',
                            "reportId": "474622176897192348",
                            "viewportParams": [
                                {
                                    "key": "0",
                                    "name": "prisoner_id",
                                    "type": "dynamic",
                                    "value": "criminalId"
                                }
                            ],
                            "dataAnalysis": ''
                        },
                        {
                            "id": "b8a49d81-5adf-11ef-9674-424980545fed",
                            "solutionCode": "deyang",
                            "name": "interview",
                            "viewport": "Fc1InterviewAssistedResultQuer",
                            "type": 0,
                            "script": '',
                            "reportId": "474622176897192348",
                            "viewportParams": [
                                {
                                    "key": "0",
                                    "name": "prisoner_id",
                                    "type": "dynamic",
                                    "value": "criminalId"
                                },
                                {
                                    "key": "1",
                                    "name": "assessment_id",
                                    "type": "dynamic",
                                    "value": "businessId"
                                }
                            ],
                            "dataAnalysis": ''
                        }
                    ]
                }
