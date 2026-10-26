from Business.PrisonAssessmentSystem.Service.HuiXinService import HuiXinService


class JiaXinService(HuiXinService):
    def __init__(self):
        super().__init__()

    def jiaxin_finish_assessment(self):
        """
        完成评估
        :return:
        """
        xllb_task = None
        gtwx_task = None

        assessment_list = \
            self.service.police_package_instance_packageList(criminalId=self.users['criminal']['id'], status='RUNNING',
                                                             pageSize=100).json()['resultList']
        if not assessment_list:
            raise Exception("当前没有正在进行的评估")
        for assessment in assessment_list:
            criminal_id = assessment['criminalId']
            assessment_instance = \
                self.service.police_package_instance_instanceAndTask(packageInstanceId=assessment['id']).json()[
                    'content'][
                    0]

            for task in assessment_instance['flowTaskPO']:
                if task['flowProcessStepAliasName'] == '心理量表' and task['status'] == 'PENDING':
                    xllb_data = \
                        self.service.SxjkBaseInfoReportQuery(criminalId=criminal_id, flowInstanceId=task['id']).json()[
                            'resultList'][0]
                    xllb_task = task['afpTaskId']

                if task['flowProcessStepAliasName'] == '个体危险性问卷' and task['status'] == 'PENDING':
                    gtwx_data = \
                        self.service.GtwxxBaseInfoReportQuery(criminalId=criminal_id, flowInstanceId=task['id']).json()[
                            'resultList'][0]
                    gtwx_task = task['afpTaskId']

            if xllb_task:
                xllb_sheet = self.service.police_sheet_task(xllb_task).json()
                formId = xllb_sheet['formId']

                xllb_sheet_data = {
                    "data": {**{
                        "crimeNameField": assessment_instance['criminalName'],
                        "pusherField": [self.users["prison_police"]["username"]],
                        "crimeIdField": [
                            assessment_instance['criminalId'],
                        ],
                        "instanceField": assessment_instance['id'],
                        "field8pdalms2h0": "<p><strong class=\"ql-size-large\">六</strong><span class=\"ql-size-large\">、请按照你的第一印象，</span><strong class=\"ql-size-large\">选择符合你自身情况的选项</strong><span class=\"ql-size-large\">，并在你认为符合的选项下打勾。</span></p>",
                        "fielddopg47feb8": "<p><strong class=\"ql-size-large\" style=\"color: rgb(0, 0, 0);\">五、</strong><span class=\"ql-size-large\" style=\"color: rgb(0, 0, 0);\">以下3个句子，每个句子后面各有7个答案。请根据你的实际情况，</span><strong class=\"ql-size-large\" style=\"color: rgb(0, 0, 0);\">在7个选项中选择你认为最适合自己的选项，</strong><span class=\"ql-size-large\">并在你认为符合的选项下打勾。</span></p>",
                        "field9fyldxl1qd": "<p><strong class=\"ql-size-large\">四、</strong><span class=\"ql-size-large\">以下表格中列出了一些病痛或问题，请仔细阅读每一条，然后根据最近一星期以内（或过去）的情况，</span><strong class=\"ql-size-large\">选择下列问题影响你自己或使你感到苦恼的程度</strong><span class=\"ql-size-large\">，答案无正确错误之分，请如实作答。在你认为符合的选项下打勾。</span></p>",
                        "fieldiddl75oliv": "<p><strong class=\"ql-size-large\">三、</strong><span class=\"ql-size-large\">这部分题目是对你自身情况的描述，</span><strong class=\"ql-size-large\">请从4个选项中选择一个最符合你的选项</strong><span class=\"ql-size-large\">，答案无正确错误之分，请如实填写。在你认为符合的选项下打勾。</span></p>",
                        "fieldb9dzm8gy88": "<p><strong class=\"ql-size-large\">二、</strong><span class=\"ql-size-large\">这部分的每一个题项都有1，2两个句子。请你仔细阅读每个题项的1，2两个句子,</span><strong class=\"ql-size-large\">选择你最赞同的一个句子</strong><span class=\"ql-size-large\">。答案无对错之分,请如实作答。在你认为赞同的选项上打勾</span>。</p>",
                        "timu1_58": "<p><span class=\"ql-size-large\">9. 我小时候（15岁以前）干过以下某些事情</span></p>",
                        "field1kkxii2ju2": "<p><strong class=\"ql-size-large\">一、</strong><span class=\"ql-size-large\">以下题目是对你的一些描述，在回答问题时，想想在过去的几年里你主要的感觉，思想和行为。“是”的意思是此描述一般来说对你合适，“否”的意思是此描述一般来说对你不合适，</span><strong class=\"ql-size-large\">每题只选一个答案</strong><span class=\"ql-size-large\">，不要漏选。在你认为符合的选项下打勾。</span></p>",
                        "fieldfzwmq0ocf8": "<p><span class=\"ql-size-large\">\t</span><span class=\"ql-size-large\" style=\"color: rgb(0, 0, 0);\">请认真阅读每道题目，按要求将答案填写到对应的答题卡上，其中注意力检测题请根据题目提示填写。</span><strong class=\"ql-size-large\" style=\"color: rgb(0, 0, 0);\">如实填写将有助于你的改造生涯，不认真做答将会重做。</strong></p>",
                        "timu1_1": "0",
                        "timu1_4": "0",
                        "timu1_20": "1",
                        "timu1_25": "0",
                        "timu1_27": "0",
                        "timu1_35": "0",
                        "timu1_45": "0",
                        "timu1_50": "0",
                        "timu1_58_1": "0",
                        "timu1_58_2": "0",
                        "timu1_58_3": "0",
                        "timu1_58_4": "0",
                        "timu1_58_5": "0",
                        "timu1_58_6": "0",
                        "timu1_58_7": "0",
                        "timu1_58_8": "0",
                        "timu1_58_9": "1",
                        "timu1_58_10": "0",
                        "timu1_58_11": "0",
                        "timu1_58_12": "0",
                        "timu1_58_13": "0",
                        "timu1_58_14": "0",
                        "timu1_58_15": "0",
                        "timu2_1": "0",
                        "timu2_2": "1",
                        "timu2_3": "1",
                        "timu2_4": "1",
                        "timu2_5": "0",
                        "timu2_6": "1",
                        "timu2_7": "1",
                        "timu2_8": "0",
                        "timu2_9": "1",
                        "timu2_10": "1",
                        "timu2_11": "0",
                        "timu3_1": "4",
                        "timu3_2": "1",
                        "timu3_3": "1",
                        "timu3_4": "4",
                        "timu3_5": "2",
                        "timu3_6": "1",
                        "timu3_7": "1",
                        "timu3_8": "4",
                        "timu6_1": "1",
                        "timu6_2": "5",
                        "timu6_3": "5",
                        "timu6_4": "1",
                        "timu6_5": "1",
                        "timu6_6": "5",
                        "timu6_7": "1",
                        "timu6_8": "1",
                        "timu6_9": "3",
                        "timu6_10": "3",
                        "timu6_11": "3",
                        "timu6_12": "5",
                        "timu6_13": "3",
                        "timu6_14": "1",
                        "timu6_15": "2",
                        "timu6_16": "1",
                        "timu6_17": "1",
                        "timu6_18": "1",
                        "timu6_19": "3",
                        "timu6_20": "1",
                        "timu6_21": "1",
                        "timu6_22": "1",
                        "timu6_23": "1",
                        "timu6_24": "1",
                        "timu6_25": "1",
                        "timu6_26": "1",
                        "timu6_27": "4",
                        "timu6_28": "1",
                        "timu6_29": "1",
                        "timu6_30": "1",
                        "timu6_31": "5",
                        "timu6_32": "1",
                        "timu6_33": "2",
                        "timu6_34": "5",
                        "timu9_4": "7",
                        "timu9_1": "1",
                        "timu9_2": "1",
                        "timu9_3": "1",
                        "timu9_5": "6",
                        "timu9_6": "2",
                        "timu11_1": "1",
                        "timu11_2": "6",
                        "steps0vt3s2b1me": 0,
                        "fieldzc478x4lbj": 8,
                        "criminalIdentityField": "user"
                    }, **xllb_data, },
                    "formId": formId,
                    "updateTime": ""
                }
                res = self.service.police_sheet_submit(taskId=xllb_task, data=xllb_sheet_data)
            if gtwx_task:
                gtwx_sheet = self.service.police_sheet_task(gtwx_task).json()
                formId = gtwx_sheet['formId']
                gtwx_sheet_data = {
                    "data": {**{
                        "crimeNameField":  assessment_instance['criminalName'],
                        "pusherField": [self.users["prison_police"]["username"]],
                        "crimeIdField": [
                            assessment_instance['criminalId'],
                        ],
                        "instanceField": assessment_instance['id'],
                        "fieldvme7rj19ee": "分组",
                        "fieldysjxx9hc50":  assessment_instance['criminalId'],
                        "fieldzc478x4lbj": 459,
                        "sex": "男",
                        "age": 38,
                        "hyzk": "离婚",
                        "znqk": "有子女",
                        "znxq": [
                            "有未成年子女"
                        ],
                        "wcnznqk": [
                            {
                                "fieldvmzi8rm8wq": "男",
                                "wcnzn_num": [
                                    "1"
                                ]
                            }
                        ],
                        "tbhj": [
                            "无"
                        ],
                        "soldiers_history": "否",
                        "police_history": "否",
                        "seriously1": "没当过",
                        "xdfd": "否",
                        "dbqk": [
                            "没有前面两种情况"
                        ],
                        "spth": "完全能说",
                        "jlnl": "一般",
                        "ysjtjzd": "农村",
                        "jtgjfs": "放任型(缺乏责任感，放任自由)",
                        "seriously2": "第四个",
                        "lsjl": "否",
                        "fmlhsj": "否",
                        "bljl": [
                            "留级",
                            "被欺负"
                        ],
                        "ssqk": [
                            "无"
                        ],
                        "charge": "侵犯财产罪",
                        "relationship_of_victim": "朋友",
                        "organizations": [
                            "否"
                        ],
                        "gzxx": "很没信心",
                        "bqjjzk": "较差",
                        "seriously3": "较好",
                        "bqxlqk": "好",
                        "jbqk": [
                            "无"
                        ],
                        "cxkrjl": [
                            "遭受重大资产损失"
                        ],
                        "dxsj": [
                            "子女没人照顾",
                            "老人没人照顾",
                            "家人生活困难",
                            "子女教育",
                            "婚姻变故"
                        ],
                        "stepsx4whqs94qy": 0,
                        "criminalIdentityField": "user"
                    }, **gtwx_data, },
                    "formId": formId,
                    "updateTime": ""
                }
                res = self.service.police_sheet_submit(taskId=gtwx_task, data=gtwx_sheet_data)
            print("<UNK>{}<UNK>")
        return
