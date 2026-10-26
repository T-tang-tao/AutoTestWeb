from Business.PrisonAssessmentSystem.API.HuiXin.criminal_system import CriminalSystem
from Business.PrisonAssessmentSystem.API.HuiXin.police_system import PoliceSystem


class HuiXin(CriminalSystem, PoliceSystem):
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

#
# if __name__ == "__main__":
#     h = HuiXin()
#     # h.police_batch_start(assessment.html=Assessment.in_prison_criminal_basic_information)
#     # h.police_login(user_type=HUIXIN_USER.prison_police)
#     # h.police_search_zfz_factory('pg10073021', '25ef14e08a8b4375b4984df991e18850')
#     # h.police_close_package_all(criminalId='pg10071910')
#     # h.criminal_login("pg10071910")
#     h.criminal_task_query_v2()
