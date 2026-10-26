from Business.PrisonAssessmentSystem.Data import HUIXIN_USER
from Business.PrisonAssessmentSystem.BaseCases.CriminalBase import CriminalBase

module_name = "入监所有评估"

class inmate_assessment_all_01(CriminalBase):
    def setUp(self):
        # 环境清理，关闭业务包
        self.run_step(step_name="清理环境 关闭所有任务",
                      method=self.huixin_app.police_close_package_all,
                      kwargs={"criminalId": self.criminalId,
                              'user_type': HUIXIN_USER.prison_police, })

    def testStep(self):
        # 罪犯基本信息pass
        pass


    # def check_body_heart_information(self):
    #     base_information = self.huixin_app.police_search_criminal_basic_information()
    #     init_information = self.huixin_app.police_init_body_heart_table()
    #     assert base_information['preson_area'] == init_information['personarea'], "监区不对应"
    #     assert init_information['crimeid'] == self.users['criminal']['id'], "罪犯编号不对应"
    #     assert init_information['crimename'] == self.users['criminal']['name'], "罪犯编号不对应"

    def body_heart_table(self):
        pass
