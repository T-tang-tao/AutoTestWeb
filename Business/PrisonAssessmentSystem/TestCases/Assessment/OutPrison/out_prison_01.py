from Business.PrisonAssessmentSystem.BaseCases.CriminalBase import CriminalBase
from Business.PrisonAssessmentSystem.Data import Assessment, HUIXIN_USER, ProcessNode, Process
from Business.PrisonAssessmentSystem.Data.audit_submit import AuditSubmitDataFactory
from TestRunner.core.Base import StepStatus

case_name = "出监评估"
class out_prison_01(CriminalBase):
    """
    低
    """

    def setUp(self):
        super().setUp()

    def defineSteps(self):
        assessment = Assessment.出监评估
        audit_submit_factory = AuditSubmitDataFactory(self.huixin_server)

        # 环境清理，关闭业务包
        self.def_step(step_name="清理环境 关闭出监评估",
                      method=self.huixin_server.police_close_package,
                      kwargs={'user_type': HUIXIN_USER.prison_police
                          , 'assessment': assessment, })

        self.def_step(step_name='【监狱民警】发起出监评估',
                      method=self.huixin_server.police_begin_assessment,
                      kwargs={"assessment": assessment})
        #
        # self.def_step(step_name='【状态校验】出监评估—再犯罪评估 流程完成  审核中',
        #               method=self.huixin_server.check_current_process_information,
        #               kwargs={"assessment": assessment,
        #                       'sonPackage': Assessment.出监评估_再犯罪评估,
        #                       'status': StepStatus.FINISHED})

        self.def_step(step_name='【民警审核】再犯罪评估审核',
                      method=self.huixin_server.police_audit_submit,
                      kwargs={
                          "data": audit_submit_factory.create_out_zfz_audit_data(
                              process=Process.出监_再犯罪审核,
                              user_type=HUIXIN_USER.prison_police
                          )})

        self.def_step(step_name='【领导审核】再犯罪评估审核',
                      method=self.huixin_server.police_audit_submit,
                      kwargs={
                          "data": audit_submit_factory.create_out_zfz_audit_data(
                              process=Process.出监_再犯罪审核,
                              user_type=HUIXIN_USER.leader_police
                          )})
        self.def_step(step_name='【评估中心审核】再犯罪评估审核',
                      method=self.huixin_server.police_audit_submit,
                      kwargs={
                          "data": audit_submit_factory.create_out_zfz_audit_data(
                              process=Process.出监_再犯罪审核,
                              user_type=HUIXIN_USER.assessment_center
                          )})
