from Business.PrisonAssessmentSystem.BaseCases.CriminalBase import CriminalBase
from Business.PrisonAssessmentSystem.Data import Assessment, HUIXIN_USER, ProcessNode
from Business.PrisonAssessmentSystem.Data.audit_submit import AuditSubmitDataFactory
from Business.PrisonAssessmentSystem.Data.sheet_submit import SheetSubmitDataFactory
from TestRunner.core.Base import StepStatus

case_name = '入监_身心健康评估'


class inmate_assessment_body_heart_healthy_01(CriminalBase):
    def setUp(self):
        super().setUp()

    def defineSteps(self):
        assessment = Assessment.入监_身心健康评估
        sheet_submit_factory = SheetSubmitDataFactory(self.huixin_server)

        # 环境清理，关闭业务包
        self.def_step(step_name="清理环境 关闭入监_身心健康",
                      method=self.huixin_server.police_close_package,
                      kwargs={'user_type': HUIXIN_USER.prison_police
                          , 'assessment': assessment, })

        self.def_step(step_name='【监狱民警】发起入监个体危险性评估',
                      method=self.huixin_server.police_begin_assessment,
                      kwargs={"assessment": assessment})


        self.def_step(step_name='【罪犯填写】身心健康评估量表',
                      method=self.huixin_server.criminal_write_sheet,
                      kwargs={
                          "data": sheet_submit_factory.create_heart_healthy_data_01()})

        #
        # self.def_step(step_name='【状态校验】身心健康评估量表  进行中',
        #               method=self.huixin_server.check_current_process_information,
        #               kwargs={"assessment": assessment,
        #                       'processNode': ProcessNode.身心健康评估量表,
        #                       'status': StepStatus.PENDING})
        #
        # self.def_step(step_name='【民警填写】身心健康评估量表',
        #               method=self.huixin_server.police_write_sheet_submit,
        #               kwargs={
        #                   "data": sheet_submit_factory.create_heart_healthy_data_01()})

        self.def_step(step_name='【状态校验】入监身心健康流程  完成',
                      method=self.check_package_process_status)
