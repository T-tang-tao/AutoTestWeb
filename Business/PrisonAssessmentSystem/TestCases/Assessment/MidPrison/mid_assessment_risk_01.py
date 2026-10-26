from sys import audit

from Business.PrisonAssessmentSystem.BaseCases.CriminalBase import CriminalBase
from Business.PrisonAssessmentSystem.Data import Assessment, Process, ProcessNode, ProcessStepStatus, HUIXIN_USER
from Business.PrisonAssessmentSystem.Data.audit_submit import AuditSubmitDataFactory
from Business.PrisonAssessmentSystem.Data.mid_prison import mid_DataFactory
from Business.PrisonAssessmentSystem.Data.sheet_submit import SheetSubmitDataFactory
from TestRunner.core.Base import StepStatus

case_name = "中期_个体危险性评估"


class mid_assessment_risk_01(CriminalBase):
    """
    低
    """

    def defineSteps(self):
        assessment = Assessment.中期_个体危险性评估
        sheet_submit_factory = SheetSubmitDataFactory(self.huixin_server)
        audit_submit_factory = AuditSubmitDataFactory(self.huixin_server)

        # 环境清理，关闭业务包
        self.def_step(step_name="清理环境 关闭入监_罪犯基本信息采集",
                      method=self.huixin_server.police_close_package,
                      kwargs={'user_type': HUIXIN_USER.prison_police
                          , 'assessment': assessment, })
        #
        self.def_step(step_name='【监狱民警】发起中期个体危险性评估',
                      method=self.huixin_server.police_begin_assessment,
                      kwargs={"assessment": assessment})

        self.def_step(step_name='【状态校验】罪犯行为观察表  进行中',
                      method=self.huixin_server.check_current_process_information,
                      kwargs={"assessment": assessment,
                              'processNode': ProcessNode.罪犯行为观察表,
                              'status': StepStatus.PENDING})

        self.def_step(step_name='【民警填写】罪犯行为观察表',
                      method=self.huixin_server.police_write_sheet_submit,
                      kwargs={
                          "data": sheet_submit_factory.create_criminal_behavior_data_01()})

        self.def_step(step_name='【状态校验】个体危险性中期评估审批表  进行中',
                      method=self.huixin_server.check_current_process_information,
                      kwargs={"assessment": assessment,
                              'processNode': ProcessNode.个体危险性中期评估审批表,
                              'status': StepStatus.PENDING})

        self.def_step(step_name='【民警填写】个体危险性中期评估审批表',
                      method=self.huixin_server.police_write_sheet_submit,
                      kwargs={
                          "data": sheet_submit_factory.create_personality_risk_mid_audit_data()})

        self.def_step(step_name='【状态校验】个体危险性中期评估审批表  审核中',
                      method=self.huixin_server.check_current_process_information,
                      kwargs={"assessment": assessment,
                              'status': StepStatus.FINISHED})

        self.def_step(step_name='【民警审核】个体危险性中期评估审核',
                      method=self.huixin_server.police_audit_submit,
                      kwargs={
                          "data": audit_submit_factory.create_middle_gtwx_audit_data(
                              process=Process.审核流程_个体危险性评估_中期,
                              user_type=HUIXIN_USER.prison_police
                          )})

        self.def_step(step_name='【领导审核】个体危险性中期评估审核',
                      method=self.huixin_server.police_audit_submit,
                      kwargs={
                          "data": audit_submit_factory.create_middle_gtwx_audit_data(
                              process=Process.审核流程_个体危险性评估_中期,
                              user_type=HUIXIN_USER.leader_police
                          )})

        self.def_step(step_name='【评估中心审核】个体危险性中期评估审批',
                      method=self.huixin_server.police_audit_submit,
                      kwargs={
                          "data": audit_submit_factory.create_middle_gtwx_audit_data(
                              process=Process.审核流程_个体危险性评估_中期,
                              user_type=HUIXIN_USER.assessment_center
                          )})
