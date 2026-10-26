from Business.PrisonAssessmentSystem.Service.HuiXinService.CriminalService import CriminalService
from Business.PrisonAssessmentSystem.Service.HuiXinService.PoliceService import PoliceService


class HuiXinService(CriminalService, PoliceService):
    def __init__(self):
        super().__init__()
        # 发起评估  当前流程信息
        self.current_process_information = {
            "processId": "",  # 流程ID
            "flowInstanceId": "",
            "criminalId": "",
            "criminalName": '',
            "packageInstanceId": "",
            "message": '',
            "packageCode": "",
            "packageName": '',
            "flowInstanceName": '',
            'audit_user': {},# 审核人
        }
