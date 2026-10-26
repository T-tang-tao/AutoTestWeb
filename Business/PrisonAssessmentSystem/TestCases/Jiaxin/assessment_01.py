from Business.PrisonAssessmentSystem.BaseCases.CriminalBase import CriminalBase
from Business.PrisonAssessmentSystem.BaseCases.CriminalBaseJiaXin import CriminalBaseJiaXin
from Business.PrisonAssessmentSystem.Data import Assessment, HUIXIN_USER, ProcessNode, Process
from Business.PrisonAssessmentSystem.Data.audit_submit import AuditSubmitDataFactory
from TestRunner.core.Base import StepStatus

class assessment_01(CriminalBaseJiaXin):
    """
    低
    """

    def defineSteps(self):
        # 环境清理，关闭业务包
        self.def_step(step_name="清理环境 关闭出监评估",
                      method=self.huixin_server.jiaxin_finish_assessment,)
