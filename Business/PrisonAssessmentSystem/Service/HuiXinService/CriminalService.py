from Business.PrisonAssessmentSystem.API.HuiXin.CriminalApi import CriminalApi
from Business.PrisonAssessmentSystem.Service.HuiXinService.InitHuiXin import InitHuiXin, global_retry


class CriminalService(InitHuiXin):
    """罪犯服务类"""

    def __init__(self):
        super().__init__()
        self.criminal_service = CriminalApi()

    def criminal_write_sheet(self, data):
        """
        罪犯填写写sheet
        :return:
        """
        # 查找任务
        afpTaskId = data.pop('afpTaskId')
        res = self.criminal_service.criminal_sheet_submit(afpTaskId, data)
        assert res.status_code == 200, '罪犯填写报表失败'

    @global_retry()
    def criminal_pre_sheet_submit_info(self, cbStepName):
        """
        罪犯填写写sheet前的数据
        :return:
        """
        # 查找任务
        res = self.criminal_service.criminal_query_taskV2()
        if res.status_code == 200:
            process_list = res.json()['resultList'][0]['taskVOS']
        else:
            raise ValueError("查询任务失败")
        process_info = next(
            (p for p in process_list if p['cbStepName'] == cbStepName),
            None
        )
        if not process_info:
            raise ValueError(f"未找到【{cbStepName}】流程信息")

        criminal_process = self.criminal_service.criminal_sheet_task(process_info['afpTaskId'])
        if criminal_process.status_code == 200:
            task_info = criminal_process.json()
        else:
            raise ValueError("查询任务失败")
        return process_info['afpTaskId'], task_info
