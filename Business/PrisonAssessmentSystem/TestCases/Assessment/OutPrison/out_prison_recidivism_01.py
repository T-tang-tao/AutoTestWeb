from Business.PrisonAssessmentSystem.Data import Assessment, ProcessStepStatus, HUIXIN_USER
from Business.PrisonAssessmentSystem.Data.audit import audit_out_prison_recidivism_table
from Business.PrisonAssessmentSystem.BaseCases.CriminalBase import CriminalBase


class out_prison_recidivism_01(CriminalBase):
    """
    低
    """

    def setUp(self):
        # 环境清理，关闭业务包
        self.run_step(step_name="清理环境 关闭出监评估_再犯罪评",
                      method=self.huixin_app.police_close_package,
                      kwargs={'assessment.html': Assessment.出监评估_再犯罪评估, })

        pass

    def testStep(self):
        self.run_step(step_name='发起出监评估_再犯罪评',
                      method=self.huixin_app.police_batch_start,
                      kwargs={"assessment.html": Assessment.出监评估_再犯罪评估,
                              "criminalId": self.criminalId})

        self.run_step(step_name='出监评估_再犯罪评状态校验',
                      method=self.check_process_status,
                      kwargs={
                          'status': ProcessStepStatus.FINISHED,
                      })

        self.run_step(step_name='【民警审核】出监评估_再犯罪评审批',
                      method=self.huixin_app.police_audit_submit,
                      kwargs={
                          "data": audit_out_prison_recidivism_table(
                              audit_level='一般',
                              huixin_app=self.huixin_app,
                          ), })

        self.run_step(step_name='【监狱领导审核】出监评估_再犯罪评审批',
                      method=self.huixin_app.police_audit_submit,
                      kwargs={
                          "data": audit_out_prison_recidivism_table(
                              audit_level='一般', user_type=HUIXIN_USER.leader_police,
                              huixin_app=self.huixin_app,
                          ), })
        #
        self.run_step(step_name='【评估中心审核】出监评估_再犯罪评审批',
                      method=self.huixin_app.police_audit_submit,
                      kwargs={
                          "data": audit_out_prison_recidivism_table(
                              audit_level='一般', user_type=HUIXIN_USER.assessment_center,
                              huixin_app=self.huixin_app,
                          ), })

        self.run_step(step_name='出监评估_再犯罪评状态校验',
                      method=self.check_process_status,
                      kwargs={
                          'status': ProcessStepStatus.FINISHED,
                      })
