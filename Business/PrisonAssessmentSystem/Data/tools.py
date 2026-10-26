from Business.PrisonAssessmentSystem.Service.HuiXinService import HuiXinService


class ToolsFactory:
    def __init__(self, huiXinService: HuiXinService):
        self.huixin_server = huiXinService
        self.audit_user = {}
