from Business.PrisonAssessmentSystem.BaseCases.CriminalBase import CriminalBase
from Business.PrisonAssessmentSystem.Data import Assessment, HUIXIN_USER
from Business.PrisonAssessmentSystem.Data.sheet_submit import SheetSubmitDataFactory

case_name = "入监_职业技能评估"
class inmate_assessment_vocational_skills_01(CriminalBase):

    def setUp(self):
        super().setUp()

    def defineSteps(self):
        assessment = Assessment.入监_职业技能评估

        # 环境清理，关闭业务包
        self.def_step(step_name="清理环境 关闭入监_职业技能评估",
                      method=self.huixin_server.police_close_package,
                      kwargs={'user_type': HUIXIN_USER.prison_police
                          , 'assessment': assessment, })

        self.def_step(step_name='【监狱民警】发起入监职业技能评估',
                      method=self.huixin_server.police_begin_assessment,
                      kwargs={"assessment": assessment})


        self.def_step(step_name='【状态校验】职业技能评估流程  完成',
                      method=self.check_package_process_status)
