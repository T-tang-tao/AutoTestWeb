from Business.PrisonAssessmentSystem.BaseCases.CriminalBase import CriminalBase
from Business.PrisonAssessmentSystem.Data import Assessment, HUIXIN_USER, ProcessNode
from Business.PrisonAssessmentSystem.Data.mid_prison import mid_DataFactory
from TestRunner.core.Base import StepStatus


class middle_assessment_confession_reform_01(CriminalBase):
    """
    低
    """
    def setUp(self):
        super().setUp()

    def defineSteps(self):
        assessment = Assessment.中期_认罪悔改表现评估
        DataFactory = mid_DataFactory(self.huixin_server)

        # 环境清理，关闭业务包
        self.def_step(step_name="清理环境 关闭中期_认罪悔改表现评估",
                      method=self.huixin_server.police_close_package,
                      kwargs={'user_type': HUIXIN_USER.prison_police
                          , 'assessment': assessment, })

        self.def_step(step_name='【监狱民警】发起中期_认罪悔改表现评估',
                      method=self.huixin_server.police_begin_assessment,
                      kwargs={"assessment": assessment})

        # self.def_step(step_name='【状态校验】认罪悔改表现评估  进行中',
        #               method=self.huixin_server.check_current_process_information,
        #               kwargs={"assessment": assessment,
        #                       'processNode': ProcessNode.认罪悔改表现评估,
        #                       'status': StepStatus.PENDING})
        # # #
        # self.def_step(step_name='【医生民警填写】体检表',
        #               method=self.huixin_server.police_write_sheet_submit,
        #               kwargs={
        #                   "data": DataFactory.create_police_interview_data()})
        # #
        # self.def_step(step_name='【状态校验】中期_访谈辅助评估流程  完成',
        #                       method=self.check_package_process_status)
