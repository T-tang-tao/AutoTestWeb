from Business.PrisonAssessmentSystem.BaseCases.CriminalBase import CriminalBase
from Business.PrisonAssessmentSystem.Data import Assessment, HUIXIN_USER, ProcessNode
from Business.PrisonAssessmentSystem.Data.mid_prison import mid_DataFactory
from TestRunner.core.Base import StepStatus


class middle_assessment_body_heart_healthy_01(CriminalBase):
    """
    低
    """

    def setUp(self):
        super().setUp()

    def defineSteps(self):
        assessment = Assessment.中期_身心健康评估
        DataFactory = mid_DataFactory(self.huixin_server)

        # 环境清理，关闭业务包
        self.def_step(step_name="清理环境 关闭中期_身心健康",
                      method=self.huixin_server.police_close_package,
                      kwargs={'user_type': HUIXIN_USER.prison_police
                          , 'assessment': assessment, })

        self.def_step(step_name='【监狱民警】发起中期_身心健康评估',
                      method=self.huixin_server.police_begin_assessment,
                      kwargs={"assessment": assessment})

        self.def_step(step_name='【罪犯填写】罪犯基本信息采集表',
                      method=self.huixin_server.criminal_write_sheet,
                      kwargs={
                          "data": DataFactory.create_criminal_healthy_data()})
        #
        self.def_step(step_name='【状态校验】中期_身心健康评估流程  完成',
                      method=self.check_package_process_status)
