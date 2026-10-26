from Business.PrisonAssessmentSystem.BaseCases.CriminalBase import CriminalBase
from Business.PrisonAssessmentSystem.Data import ProcessNode, Assessment, ProcessStepStatus, HUIXIN_USER, Process
from Business.PrisonAssessmentSystem.Data.audit_submit import AuditSubmitDataFactory
from Business.PrisonAssessmentSystem.Data.in_prison import In_DataFactory
from Business.PrisonAssessmentSystem.Data.sheet_submit import SheetSubmitDataFactory
from TestRunner.core.Base import StepStatus

case_name = '入监_个体危险性评估'


class inmate_assessment_personal_risk_01(CriminalBase):
    # 入监 个体危险性评估
    # 发起个体危险性评估

    def setUp(self):
        # res = self.db.select(
        #     table="ja_cb_prison_library",
        #     where={"criminal_id": self.criminalId, "assessment_type": Assessment.入监_个体危险性评估}
        # )[0]
        super().setUp()

    def defineSteps(self):
        assessment = Assessment.入监_个体危险性评估
        sheet_submit_factory = SheetSubmitDataFactory(self.huixin_server)
        audit_submit_factory = AuditSubmitDataFactory(self.huixin_server)

        # 环境清理，关闭业务包
        self.def_step(step_name="清理环境 关闭入监_个体危险性评估",
                      method=self.huixin_server.police_close_package,
                      kwargs={'user_type': HUIXIN_USER.prison_police
                          , 'assessment': assessment, })

        self.def_step(step_name='【监狱民警】发起入监个体危险性评估',
                      method=self.huixin_server.police_begin_assessment,
                      kwargs={"assessment": assessment})


        self.def_step(step_name='【状态校验】犯罪情况  进行中',
                      method=self.huixin_server.check_current_process_information,
                      kwargs={"assessment": assessment,
                              'processNode': ProcessNode.犯罪情况,
                              'status': StepStatus.PENDING})

        self.def_step(step_name='【民警填写】犯罪情况',
                      method=self.huixin_server.police_write_sheet_submit,
                      kwargs={
                          "data": sheet_submit_factory.create_inmate_fzqk_data()})

        self.def_step(step_name='【状态校验】个体危险性入监流程  完成',
                      method=self.huixin_server.check_current_process_information,
                      kwargs={"assessment": assessment,
                              'status': StepStatus.FINISHED})

        self.def_step(step_name='【民警审核】个体危险性入监评估流程 审批',
                      method=self.huixin_server.police_audit_submit,
                      kwargs={
                          "data": audit_submit_factory.create_inmate_gtwx_audit_data(
                              process=Process.入监_个体危险性评估审批流程,
                              user_type=HUIXIN_USER.prison_police
                          )})

        self.def_step(step_name='【领导审核】个体危险性入监评估流程  审批',
                      method=self.huixin_server.police_audit_submit,
                      kwargs={
                          "data": audit_submit_factory.create_inmate_gtwx_audit_data(
                              process=Process.入监_个体危险性评估审批流程,
                              user_type=HUIXIN_USER.leader_police
                          )})

        self.def_step(step_name='【评估中心审核】个体危险性入监评估流程 审批',
                      method=self.huixin_server.police_audit_submit,
                      kwargs={
                          "data": audit_submit_factory.create_inmate_gtwx_audit_data(
                              process=Process.入监_个体危险性评估审批流程,
                              user_type=HUIXIN_USER.assessment_center
                          )})

        self.def_step(step_name='【审核流程校验】入监个体危险性',
                      method=self.check_audit_status,)
