from Business.PrisonAssessmentSystem.BaseCases.CriminalBase import CriminalBase
from Business.PrisonAssessmentSystem.Data import Assessment, HUIXIN_USER, ProcessNode, Process
from Business.PrisonAssessmentSystem.Data.audit_submit import AuditSubmitDataFactory
from Business.PrisonAssessmentSystem.Data.in_prison import In_DataFactory
from TestRunner.core.Base import StepStatus

case_name = "入监_罪犯基本信息采集"


class inmate_assessment_criminal_base_info_01(CriminalBase):
    def setUp(self):
        super().setUp()

    def defineSteps(self):
        # 初始化数据工厂
        Data = In_DataFactory(self.huixin_server)
        AuditFactory = AuditSubmitDataFactory(self.huixin_server)
        assessment = Assessment.入监_罪犯基本信息采集
        # 环境清理，关闭业务包
        self.def_step(step_name="清理环境 关闭入监_罪犯基本信息采集",
                      method=self.huixin_server.police_close_package,
                      kwargs={'user_type': HUIXIN_USER.prison_police
                          , 'assessment': assessment, })

        self.def_step(step_name='【监狱民警】发起入监评估',
                      method=self.huixin_server.police_begin_assessment,
                      kwargs={"assessment": assessment})

        self.def_step(step_name='【状态校验】监狱医生 身心健康_辅助检查详细指标  进行中',
                      method=self.huixin_server.check_current_process_information,
                      kwargs={"assessment": Assessment.入监_罪犯基本信息采集_民警,
                              'processNode': ProcessNode.身心健康_辅助检查详细指标,
                              'user_type': HUIXIN_USER.doctor_police,
                              'status': StepStatus.PENDING})
        #
        self.def_step(
            step_name='【监狱医生】填写身心健康_辅助检查详细指标',
            method=self.huixin_server.police_write_sheet_submit,
            kwargs={
                "data": Data.create_in_prison_body_heart_health_data(
                    processNode=ProcessNode.身心健康_辅助检查详细指标
                )
            }
        )
        self.def_step(step_name='【状态校验】监狱医生 入监体检表  进行中',
                      method=self.huixin_server.check_current_process_information,
                      kwargs={"assessment": Assessment.入监_罪犯基本信息采集_民警,
                              'processNode': ProcessNode.入监体检表,
                              'user_type': HUIXIN_USER.doctor_police,
                              'status': StepStatus.PENDING})
        # #
        self.def_step(step_name='【医生民警填写】体检表',
                      method=self.huixin_server.police_write_sheet_submit,
                      kwargs={
                          "data": Data.create_in_prison_medical_form_data(processNode=ProcessNode.入监体检表)})
        # #
        self.def_step(step_name='【罪犯填写】改造难易-入监问卷',
                      method=self.huixin_server.criminal_write_sheet,
                      kwargs={
                          "data": Data.create_in_prison_transformation_difficultly()})

        self.def_step(step_name='【罪犯填写】罪犯基本信息采集表',
                      method=self.huixin_server.criminal_write_sheet,
                      kwargs={
                          "data": Data.create_inmate_criminal_base_info_table()})

        self.def_step(step_name='【罪犯填写】罪犯行为测试表',
                      method=self.huixin_server.criminal_write_sheet,
                      kwargs={
                          "data": Data.create_inmate_behaviour_assessment_form(), })

        self.def_step(step_name='【状态校验】入监罪犯基本信息采集流程  完成',
                      method=self.check_package_process_status)

        self.def_step(step_name='【民警审核】入监基本信息采集',
                      method=self.huixin_server.police_audit_submit,
                      kwargs={
                          "data": AuditFactory.create_inmate_criminal_base_info(
                              process=Process.入监_基本信息采集审批,
                              user_type=HUIXIN_USER.prison_police
                          )})

        self.def_step(step_name='【审核流程校验】入监基本信息采集',
                      method=self.check_audit_status, )

    def body_heart_table(self):
        pass
