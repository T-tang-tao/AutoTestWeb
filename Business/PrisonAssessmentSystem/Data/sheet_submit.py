import datetime

from Business.PrisonAssessmentSystem.Service.HuiXinService import HuiXinService


class SheetSubmitDataFactory:
    """表单提交数据工厂"""

    def __init__(self, huiXinService: HuiXinService):
        self.huixin_server = huiXinService

    def create_heart_healthy_data_01(self, **kwargs):
        """创建身心健康评估数据_01"""

        def data_generator():
            try:
                # 获取流程信息
                id, node_info = self.huixin_server.criminal_pre_sheet_submit_info('身心健康评估量表')
                criminal_base_info = self.huixin_server.police_search_criminal(
                    criminalId=self.huixin_server.users['criminal']['id'])['baseinfo']
                data = {
                        "afpTaskId": id,
                    "data": {
                        "crimeNameField": criminal_base_info['name'],
                        # "pusherField": node_info['data']['criminalIdentityField'],
                        "crimeIdField": [
                            criminal_base_info['id']
                        ],
                        "instanceField": node_info['data']['instanceField'],
                        "packageInstanceId": node_info['data']['packageInstanceId'],
                        "field8pdalms2h0": "<p><span class=\"ql-size-large\">十一、请按照你的第一印象，</span><strong class=\"ql-size-large\">选择符合你自身情况的选项。</strong></p>",
                        "fieldhly6htsmq6": "<p><strong class=\"ql-size-large\">十、</strong><span class=\"ql-size-large\">当人们变得沮丧、生气或被激怒时，他们会以不同的方式表达。考虑一下你近6个月内的攻击行为（攻击行为是指当你生气或感到沮丧时出手打人和/或用言语侮辱别人或扔/破坏东西的行为），</span><strong class=\"ql-size-large\">选择一个答案</strong><span class=\"ql-size-large\">。答案无正确错误之分，请如实作答。</span></p>",
                        "fielddopg47feb8": "<p><strong class=\"ql-size-large\" style=\"color: rgb(0, 0, 0);\">九、</strong><span class=\"ql-size-large\" style=\"color: rgb(0, 0, 0);\">以下3个句子，每个句子后面各有7个答案。请根据你的实际情况，</span><strong class=\"ql-size-large\" style=\"color: rgb(0, 0, 0);\">在7个选项中选择你认为最适合自己的选项</strong><span class=\"ql-size-large\" style=\"color: rgb(0, 0, 0);\">。</span></p>",
                        "field9x8o8x4q87": "<p><strong class=\"ql-size-large\">八、</strong><span class=\"ql-size-large\">以下是我们对一些人的简单描述，请阅读每个描述，并思考每个人有多少像你或不像你，</span><strong class=\"ql-size-large\">请在6个选项中选择像你的程度。</strong></p>",
                        "fieldg9h4ggpnke": "<p><strong style=\"color: rgb(0, 0, 0);\" class=\"ql-size-large\">七、</strong><span style=\"color: rgb(0, 0, 0);\" class=\"ql-size-large\">下列题目是对你的一些描述，请根据自己的实际情况选择这个描述是否准确，</span><strong class=\"ql-size-large\" style=\"color: rgb(0, 0, 0);\">准确请选择“是”，不准确请选择“否”。</strong></p>",
                        "field9fyldxl1qd": "<p><strong class=\"ql-size-large\">六、</strong><span class=\"ql-size-large\">以下表格中列出了一些病痛或问题，请仔细阅读每一条，然后根据最近一星期以内（或过去）的情况，</span><strong class=\"ql-size-large\">选择下列问题影响你自己或使你感到苦恼的程度</strong><span class=\"ql-size-large\">，答案无正确错误之分，请如实作答。</span></p>",
                        "fieldyfo9kwh0a5": "<p><strong style=\"color: rgb(0, 0, 0);\" class=\"ql-size-large\">五、</strong><span style=\"color: rgb(0, 0, 0);\" class=\"ql-size-large\">以下题目是对你自身感受的描述，</span><strong class=\"ql-size-large\">请从4个选项中选择一个最符合你的选项</strong><span style=\"color: rgb(0, 0, 0);\" class=\"ql-size-large\">，答案无正确与错误之分，请如实回答。</span></p>",
                        "fieldppg3roshx4": "<p><strong class=\"ql-size-large\" style=\"color: rgb(0, 0, 0);\">四</strong><span class=\"ql-size-large\" style=\"color: rgb(0, 0, 0);\">、请指出以下每条描绘在多大程度上反应了你的状况，并尽量按第一反应，</span><strong class=\"ql-size-large\">从5个选项中选择一个最符合你的选项</strong><span class=\"ql-size-large\" style=\"color: rgb(0, 0, 0);\">。答案无对错只分，请如实作答。</span></p>",
                        "fieldiddl75oliv": "<p><strong class=\"ql-size-large\">三、</strong><span class=\"ql-size-large\">这部分题目是对你自身情况的描述，</span><strong class=\"ql-size-large\">请从4个选项中选择一个最符合你的选项</strong><span class=\"ql-size-large\">，答案无正确错误之分，请如实填写。</span></p>",
                        "fieldb9dzm8gy88": "<p><strong class=\"ql-size-large\">二、</strong><span class=\"ql-size-large\">这部分的每一个题项都有1，2两个句子。请你仔细阅读每个题项的1，2两个句子,</span><strong class=\"ql-size-large\">选择你最赞同的一个句子</strong><span class=\"ql-size-large\">。答案无对错之分,请如实作答。</span></p>",
                        "timu1_58": "<p><span class=\"ql-size-large\">58 .我小时候（15岁以前）干过以下某些事情</span></p>",
                        "timu1_57": "<p><span class=\"ql-size-large\">﻿57 .我凭一时冲动干过一些以下的事情以至给我带来麻烦</span></p>",
                        "field1kkxii2ju2": "<p><strong class=\"ql-size-large\">一、</strong><span class=\"ql-size-large\">以下题目是对你的一些描述，在回答问题时，想想在过去的几年里你主要的感觉，思想和行为。“是”的意思是此描述一般来说对你合适，“否”的意思是此描述一般来说对你不合适，</span><strong class=\"ql-size-large\">每题只选一个答案。</strong><span class=\"ql-size-large\">答案无对错之分，请如实作答。</span></p>",
                        "fieldfzwmq0ocf8": "<p><span class=\"ql-size-large\">\t</span><span style=\"color: rgb(0, 0, 0);\" class=\"ql-size-large\">请认真阅读每道题目，按要求将答案填写到对应的答题卡上，其中注意力检测题请根据题目提示填写。</span><strong style=\"color: rgb(0, 0, 0);\" class=\"ql-size-large\">如实填写将有助于你的改造生涯，不认真做答将会重做。</strong></p>",
                        "crimename": criminal_base_info['name'],
                        "crimeid": criminal_base_info['id'],
                        "an13": criminal_base_info['age'].replace('岁', ''),
                        "presonarea": criminal_base_info['preson_area'],
                        "timu1_1": "0",
                        "timu1_2": "1",
                        "timu1_3": "0",
                        "timu1_4": "0",
                        "timu1_5": "0",
                        "timu1_6": "0",
                        "timu1_7": "0",
                        "timu1_8": "0",
                        "timu1_9": "0",
                        "timu1_10": "0",
                        "timu1_11": "1",
                        "timu1_12": "0",
                        "timu1_13": "1",
                        "timu1_14": "0",
                        "timu1_15": "1",
                        "timu1_16": "1",
                        "timu1_17": "0",
                        "timu1_18": "0",
                        "timu1_19": "0",
                        "timu1_20": "0",
                        "timu1_21": "1",
                        "timu1_22": "1",
                        "timu1_23": "0",
                        "timu1_24": "0",
                        "timu1_25": "1",
                        "timu1_26": "0",
                        "timu1_27": "0",
                        "timu1_28": "1",
                        "timu1_29": "1",
                        "timu1_30": "0",
                        "timu1_31": "0",
                        "timu1_32": "0",
                        "timu1_33": "1",
                        "timu1_34": "0",
                        "timu1_35": "0",
                        "timu1_36": "0",
                        "timu1_37": "0",
                        "timu1_38": "0",
                        "timu1_39": "1",
                        "timu1_40": "0",
                        "timu1_41": "0",
                        "timu1_42": "0",
                        "timu1_43": "0",
                        "timu1_44": "0",
                        "timu1_45": "0",
                        "timu1_46": "0",
                        "timu1_47": "0",
                        "timu1_48": "1",
                        "timu1_49": "0",
                        "timu1_50": "0",
                        "timu1_51": "1",
                        "timu1_52": "0",
                        "timu1_53": "0",
                        "timu1_54": "1",
                        "timu1_55": "1",
                        "timu1_56": "0",
                        "timu1_57_1": "0",
                        "timu1_57_2": "0",
                        "timu1_57_3": "0",
                        "timu1_57_4": "0",
                        "timu1_57_5": "1",
                        "timu1_57_6": "1",
                        "timu1_58_1": "0",
                        "timu1_58_2": "0",
                        "timu1_58_3": "1",
                        "timu1_58_4": "0",
                        "timu1_58_5": "1",
                        "timu1_58_6": "1",
                        "timu1_58_7": "1",
                        "timu1_58_8": "0",
                        "timu1_58_9": "1",
                        "timu1_58_10": "1",
                        "timu1_58_11": "1",
                        "timu1_58_12": "1",
                        "timu1_58_13": "0",
                        "timu1_58_14": "0",
                        "timu1_58_15": "1",
                        "timu2_1": "1",
                        "timu2_2": "0",
                        "timu2_3": "1",
                        "timu2_4": "1",
                        "timu2_5": "0",
                        "timu2_6": "0",
                        "timu2_7": "0",
                        "timu2_8": "1",
                        "timu2_9": "0",
                        "timu2_10": "1",
                        "timu2_11": "1",
                        "timu3_1": "4",
                        "timu3_2": "2",
                        "timu3_3": "2",
                        "timu3_4": "2",
                        "timu3_5": "2",
                        "timu3_6": "3",
                        "timu3_7": "4",
                        "timu3_8": "4",
                        "timu4_1": "5",
                        "timu4_2": "4",
                        "timu4_3": "1",
                        "timu4_4": "3",
                        "timu4_5": "3",
                        "timu5_1": "2",
                        "timu5_2": "3",
                        "timu5_3": "2",
                        "timu5_4": "3",
                        "timu5_5": "2",
                        "timu6_1": "3",
                        "timu6_2": "3",
                        "timu6_3": "2",
                        "timu6_4": "2",
                        "timu6_5": "2",
                        "timu6_6": "4",
                        "timu6_7": "2",
                        "timu6_8": "2",
                        "timu6_9": "3",
                        "timu6_10": "2",
                        "timu6_11": "2",
                        "timu6_12": "4",
                        "timu6_13": "3",
                        "timu6_14": "3",
                        "timu6_15": "4",
                        "timu6_16": "2",
                        "timu6_17": "4",
                        "timu6_18": "4",
                        "timu6_19": "4",
                        "timu6_20": "2",
                        "timu6_21": "2",
                        "timu6_22": "3",
                        "timu6_23": "2",
                        "timu6_24": "3",
                        "timu6_25": "2",
                        "timu6_26": "2",
                        "timu6_27": "2",
                        "timu6_28": "2",
                        "timu6_29": "2",
                        "timu6_30": "2",
                        "timu6_31": "1",
                        "timu6_32": "5",
                        "timu6_33": "5",
                        "timu7_1": "0",
                        "timu7_2": "0",
                        "timu7_3": "1",
                        "timu7_4": "0",
                        "timu7_5": "0",
                        "timu7_6": "0",
                        "timu7_7": "0",
                        "timu7_8": "0",
                        "timu7_9": "0",
                        "timu7_10": "0",
                        "timu7_11": "0",
                        "timu7_12": "0",
                        "timu7_13": "0",
                        "timu7_14": "1",
                        "timu7_15": "0",
                        "timu7_16": "0",
                        "timu7_17": "0",
                        "timu7_18": "0",
                        "timu7_19": "0",
                        "timu7_20": "1",
                        "timu7_21": "1",
                        "timu7_22": "0",
                        "timu7_23": "1",
                        "timu7_24": "1",
                        "timu7_25": "1",
                        "timu7_26": "1",
                        "timu7_27": "1",
                        "timu7_28": "0",
                        "timu7_29": "0",
                        "timu7_30": "1",
                        "timu7_31": "0",
                        "timu7_32": "0",
                        "timu7_33": "1",
                        "timu7_34": "0",
                        "timu7_35": "1",
                        "timu7_36": "1",
                        "timu7_37": "0",
                        "timu7_38": "0",
                        "timu7_39": "0",
                        "timu7_40": "1",
                        "timu8_1": "2",
                        "timu8_2": "2",
                        "timu8_3": "2",
                        "timu8_4": "2",
                        "timu8_5": "2",
                        "timu8_6": "5",
                        "timu8_7": "3",
                        "timu8_8": "5",
                        "timu8_9": "2",
                        "timu8_10": "2",
                        "timu8_11": "2",
                        "timu8_12": "6",
                        "timu8_13": "5",
                        "timu8_14": "5",
                        "timu8_15": "2",
                        "timu8_16": "1",
                        "timu8_17": "4",
                        "timu8_18": "2",
                        "timu8_19": "2",
                        "timu8_20": "2",
                        "timu8_21": "2",
                        "timu9_1": "4",
                        "timu9_2": "2",
                        "timu9_3": "2",
                        "timu10_1": "4",
                        "timu10_2": "2",
                        "timu10_3": "3",
                        "timu10_4": "2",
                        "timu10_5": "2",
                        "timu10_6": "2",
                        "timu10_7": "2",
                        "timu11_1": "2",
                        "timu11_2": "2",
                        "fieldzc478x4lbj": 116,
                        "criminalIdentityField": "user"
                    },
                    "formId": node_info['formId'],
                    "updateTime": ""
                }
                return data
            except Exception as e:
                self.huixin_server.logger.error(f"创建身心健康评估数据失败，异常信息：{e}")
                raise e

        return data_generator

    def create_criminal_behavior_data_01(self, **kwargs):
        """创建罪犯行为数据_01"""

        def data_generator():
            criminal_base_info = self.huixin_server.police_search_criminal(
                criminalId=self.huixin_server.users['criminal']['id'])['baseinfo']
            node_info = self.huixin_server.current_process_information['currentNode']
            data = {
                "data": {
                    "crimeNameField": criminal_base_info['name'],
                    "pusherField": node_info['afpTaskDetail']['data']['pusherField'],
                    "crimeIdField": [
                        criminal_base_info['id']
                    ],
                    "instanceField": node_info['flowInstanceId'],
                    "criminal_behavior": {
                        "prison_area": criminal_base_info['preson_area'],
                        "observe_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "observe_qr": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "observe_police": self.huixin_server.users['prison_police']['name'],
                        "name": criminal_base_info['name'],
                        "crime_num": criminal_base_info['id'],
                        "age": criminal_base_info['age'].replace("岁", ""),
                        "xq": criminal_base_info['xq'],
                        "charges": criminal_base_info['crime_name']
                    },
                    "fieldohztlhtrti": "<p><span class=\"ql-size-large\">民警根据罪犯在本观察期内的现实表现、材料收集、信息跟踪进行综合研判和分析后，尽可能对下表每一个项目，做出准确、客观的评估判断。</span></p>",
                    "field1itocmbs9": "观察原因",
                    "observe_reason": "经教育、疏导后，该犯过激言行改善情况不佳",
                    "fieldjz0or6rpaz": "危险行为",
                    "fight": "1.未发现",
                    "injury": "1.未发现",
                    "suicide": "1.未发现",
                    "escape": "1.未发现",
                    "crime": "1.未发现",
                    "yyjfsmd": "1.未发现",
                    "wrdkyj": "1.未发现",
                    "dcqx": "1.未发现",
                    "zzwxwjp": "1.未发现",
                    "jljysd": "1.未发现",
                    "szgj": "1.未发现",
                    "yybftr": "1.未发现",
                    "fieldlp10hf6gn": "认罪悔罪",
                    "dfypjss": "4.都认可",
                    "sfss": "2.未申诉",
                    "sdtr": "1.未发现",
                    "gkyyfzs": "1.未发现",
                    "cclxqk": "1.完整履行",
                    "ldgzqk": "2.足额",
                    "fieldcsqijjbb6": "精神状态",
                    "jszt": [
                        "1.衣着整洁"
                    ],
                    "field5a4vekffv": "交流沟通情况",
                    "thljx": "2.逻辑性一般",
                    "byjcht": "2.无",
                    "bebtht": "2.无",
                    "fyxl": "2.否",
                    "fielddhebuldks": "情绪状态",
                    "qxzt": [
                        "4.情绪无变化"
                    ],
                    "fieldbi2k87ajcz": "睡眠状态",
                    "smzt": [
                        "6.正常"
                    ],
                    "fieldnau9vqj27": "生活作息规律",
                    "shzxgl": "1.正常",
                    "fieldi5bawtnf7a": "躯体表现",
                    "qtbx": [
                        "5.正常"
                    ],
                    "fieldslzmn5vbs": "狱内再犯罪",
                    "ynzfz": "2.否",
                    "fieldfmjj9aovs": "其他法律问题",
                    "sfbh": [
                        "6.否"
                    ],
                    "fieldmqbc4liazm": "观察到的其他情况 ",
                    "qtqk": "无",
                    "field6y9qvmmf2e": 99,
                    "criminalIdentityField": "user"
                },
                "formId": node_info['afpTaskDetail']['formId'],
                "updateTime": ""
            }

            return data

        return data_generator

    def create_inmate_fzqk_data(self, **kwargs):
        def data_generator():
            try:
                criminal_base_info = self.huixin_server.police_search_criminal(
                    criminalId=self.huixin_server.users['criminal']['id'])['baseinfo']
                node_info = self.huixin_server.current_process_information['currentNode']
                data = {
                    "data": {
                        "crimeNameField": criminal_base_info['name'],
                        "pusherField": node_info['afpTaskDetail']['data']['pusherField'],
                        "crimeIdField": [
                            criminal_base_info['id']
                        ],
                        "instanceField": node_info['flowInstanceId'],
                        "crimeid": criminal_base_info['id'],
                        "crimename": criminal_base_info['name'],
                        "presonarea": criminal_base_info['preson_area'],
                        "packageInstanceId": "1960968270629171201",
                        "crime_situation": {
                            "name": criminal_base_info['name'],
                            "crime_num": criminal_base_info['id'],
                            "crime_name": criminal_base_info['crime_name'],
                            "zx__type": criminal_base_info['xq'],
                            "ypxqr": criminal_base_info.get('DQXQQR', '2000-01-01 00:00:00'),
                            "fzxt": "犯罪既遂",
                            "xaflb": "重大刑事犯",
                            "ywqk": "无",
                            "record_info": {},
                            "sddj": [
                                "涉毒"
                            ],
                            "ssdj": [
                                "无"
                            ],
                            "sjzz": [
                                "否"
                            ],
                            "rztd": "承认犯罪事实，有较强的赎罪感",
                            "bdzzql": "无",
                            "mscc": "无",
                            "mspc": "无",
                            "fjqk": "无",
                            "lcza": [
                                "否"
                            ],
                            "sfczgf": "否",
                            "ybhrgx": [
                                "恋人"
                            ],
                            "jwbs_gsjd": "无",
                            "jwbs_ssldnlcdjd": "无"
                        },
                        "criminalIdentityField": "user"
                    },
                    "formId": node_info['afpTaskDetail']['formId'],
                    "updateTime": ""
                }
                return data
            except Exception as e:
                raise Exception(f'民警填写犯罪情况数据生成失败{str(e)}')

        return data_generator

    def create_personality_risk_mid_audit_data(self, **kwargs):
        def data_generator():
            try:
                criminal_base_info = self.huixin_server.police_search_criminal(
                    criminalId=self.huixin_server.users['criminal']['id'])['baseinfo']
                node_info = self.huixin_server.current_process_information['currentNode']
                data = {
                    "data": {
                        "crimeNameField": criminal_base_info['name'],
                        "pusherField": node_info['afpTaskDetail']['data']['pusherField'],
                        "crimeIdField": [
                            criminal_base_info['id']
                        ],
                        "instanceField": node_info['flowInstanceId'],
                        "crimeid": criminal_base_info['id'],
                        "crimename": criminal_base_info['name'],
                        "presonarea": criminal_base_info['preson_area'],
                        "suicide_tendency": [
                            kwargs.get('suicide_tendency', "低")
                        ],
                        "violent_tendency": [
                            kwargs.get('violent_tendency', "低")
                        ],
                        "escape_tendency": [
                            kwargs.get('escape_tendency', "低")
                        ],
                        "danger_level": [
                            kwargs.get('danger_level', "低")
                        ],
                        "scale_risk_factors": "中低度，暂不填写",
                        "act_observ_danger_level": "低",
                        "negative_event_impact_level": "无",
                        "evaluation_reason": "经教育、疏导后，该犯过激言行改善情况不佳",
                        "now_suicide_tendency": [
                            kwargs.get('suicide_tendency', "低")
                        ],
                        "now_violent_tendency": [
                            kwargs.get('violent_tendency', "低")
                        ],
                        "now_escape_tendency": [
                            kwargs.get('escape_tendency', "低")
                        ],
                        "now_danger_level": [
                            kwargs.get('danger_level', "低")
                        ],
                        "finishing_people": self.huixin_server.users['prison_police']['name'],
                        "criminalIdentityField": "user"
                    },
                    "formId": node_info['afpTaskDetail']['formId'],
                    "updateTime": ""
                }
                return data
            except Exception as e:
                raise Exception(f'创建个人危险中期评估审批数据失败：{str(e)}')

        return data_generator

    def create_inmate_physical_data(self, **kwargs):
        """Create physical examination data from explicit environment values."""
        required_keys = (
            "criminal_id",
            "package_instance_id",
            "instance_id",
            "form_id",
        )
        missing_keys = [key for key in required_keys if not kwargs.get(key)]
        if missing_keys:
            raise ValueError(
                "Missing required arguments: " + ", ".join(missing_keys)
            )

        def data_generator():
            criminal_base_info = self.huixin_server.police_search_criminal(
                criminalId=kwargs["criminal_id"])['baseinfo']
            pusher_field = kwargs.get("pusher_field") or [
                self.huixin_server.users["prison_police"]["username"]
            ]
            if isinstance(pusher_field, str):
                pusher_field = [pusher_field]
            data = {
                "data": {
                    "crimeNameField": criminal_base_info['name'],
                    "pusherField": pusher_field,
                    "packageInstanceId": kwargs["package_instance_id"],
                    "crimeIdField": [
                        kwargs["criminal_id"]
                    ],
                    "instanceField": kwargs["instance_id"],
                    "crimename": criminal_base_info['name'],
                    "personarea": criminal_base_info['preson_area'],
                    "fieldbundr24qme": "血常规",
                    "wbc": kwargs.get('wbc', 6.5),
                    "lymph": kwargs.get('lymph', 30),
                    "gran": kwargs.get('gran', 60),
                    "rbc": kwargs.get('rbc', 4.5),
                    "hgb": kwargs.get('hgb', 135),
                    "plt": kwargs.get('plt', 200),
                    "xcg_report_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "fieldun8m2d1o8h": "肝功",
                    "alt": kwargs.get('alt', 20),
                    "ast": kwargs.get('ast', 22),
                    "ast_alt_ratio": kwargs.get('ast_alt_ratio', 1),
                    "tp": kwargs.get('tp', 70),
                    "alb": kwargs.get('alb', 45),
                    "glo": kwargs.get('glo', 25),
                    "gg_report_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "criminalIdentityField": "user"
                },
                "formId": kwargs["form_id"],
                "updateTime": kwargs.get("update_time", "")
            }
            return data
