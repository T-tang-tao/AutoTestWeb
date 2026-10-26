from Business.PrisonAssessmentSystem.Data import *
from Business.PrisonAssessmentSystem.Data.out_prison import out_police_social_table, out_criminal_social_table, \
    out_police_social_table_02, out_criminal_social_table_02
from Business.PrisonAssessmentSystem.BaseCases.CriminalBase import CriminalBase


class out_prison_social_01(CriminalBase):
    """
    低
    """

    def setUp(self):
        # 环境清理，关闭业务包
        self.run_step(step_name="清理环境 关闭出监评估_社会适应性评估",
                      method=self.huixin_app.police_close_package,
                      kwargs={'assessment.html': Assessment.出监评估_社会适应性评估, })

        pass

    def testStep(self):
        self.run_step(step_name='发起出监评估_社会适应性评估',
                      method=self.huixin_app.police_batch_start,
                      kwargs={"assessment.html": Assessment.出监评估_社会适应性评估,
                              "criminalId": self.criminalId})

        self.run_step(step_name='【民警填写】社会适应性民警他评问卷',
                      method=self.huixin_app.police_sheet_submit,
                      kwargs={
                          'processNode': ProcessNode.社会适应性民警他评问卷,
                          "data": out_police_social_table(huixin_app=self.huixin_app,
                                                          processNode=ProcessNode.社会适应性民警他评问卷)})

        self.run_step(step_name='【罪犯填写】社会适应性评估量表',
                      method=self.huixin_app.criminal_sheet_submit,
                      kwargs={
                          "data": out_criminal_social_table(huixin_app=self.huixin_app, ), })


        self.run_step(step_name='【罪犯填写】社会适应性调查出监问卷',
                      method=self.huixin_app.criminal_sheet_submit,
                      kwargs={
                          "data": out_criminal_social_table_02(huixin_app=self.huixin_app, ), })

        self.run_step(step_name='出监评估_社会适应性评估',
                      method=self.check_process_status,
                      kwargs={
                          'status': ProcessStepStatus.FINISHED,
                      })
