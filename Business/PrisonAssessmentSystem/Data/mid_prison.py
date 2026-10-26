from datetime import datetime

from Business.PrisonAssessmentSystem.API import HuiXin
from Business.PrisonAssessmentSystem.Data import ProcessNode, HUIXIN_USER
from Business.PrisonAssessmentSystem.Service.HuiXinService import HuiXinService
from utils import Common


class mid_DataFactory():
    """数据工厂类：统一管理所有测试数据的生成逻辑"""

    def __init__(self, huiXinService: HuiXinService):
        self.huixin_server = huiXinService
        self.audit_user = {}

    # ------------------------------
    # 犯罪行为观察表
    # ------------------------------
    # def create_criminal_behavior_data(self,huixin_server: HuiXinService):
    #     """生成【罪犯行为观察表】数据"""
    #     def data_generator():
    #         try:
    #             # 获取流程信息和罪犯基本信息
    #             huixin_server.logger.debug("===== 开始执行 data_generator 生成数据 =====")
    #             process_info = huixin_app.police_get_current_process_information(
    #                 processNode=ProcessNode.罪犯行为观察表
    #             )
    #             criminal_info = huixin_app.criminal_information['baseinfo']
    #             return {
    #                 "data": {
    #                     "crimeNameField": criminal_info['name'],
    #                     "pusherField": process_info['data']['pusherField'],
    #                     "crimeIdField": [criminal_info['id']],
    #                     "instanceField": process_info['data']['instanceField'],
    #                     "criminal_behavior": {
    #                         "prison_area": criminal_info['preson_area'],
    #                         "observe_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    #                         "observe_qr": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    #                         "observe_police": huixin_app.users['prison_police']['name'],
    #                         "name": criminal_info['name'],
    #                         "crime_num": criminal_info['id'],
    #                         "age": criminal_info['age'],
    #                         "xq": criminal_info['xq'],
    #                         "charges": criminal_info['crime_name']
    #                     },
    #                     "fieldohztlhtrti": "<p><span class=\"ql-size-large\">民警根据罪犯在本观察期内的现实表现、材料收集、信息跟踪进行综合研判和分析后，尽可能对下表每一个项目，做出准确、客观的评估判断。</span></p>",
    #                     "field1itocmbs9": "观察原因",
    #                     "observe_reason": "经教育、疏导后，该犯过激言行改善情况不佳",
    #                     "fieldjz0or6rpaz": "危险行为",
    #                     "fight": "1.未发现",
    #                     "injury": "1.未发现",
    #                     "suicide": "1.未发现",
    #                     "escape": "1.未发现",
    #                     "crime": "1.未发现",
    #                     "yyjfsmd": "1.未发现",
    #                     "wrdkyj": "1.未发现",
    #                     "dcqx": "1.未发现",
    #                     "zzwxwjp": "1.未发现",
    #                     "jljysd": "1.未发现",
    #                     "szgj": "1.未发现",
    #                     "yybftr": "1.未发现",
    #                     "fieldlp10hf6gn": "认罪悔罪",
    #                     "dfypjss": "4.都认可",
    #                     "sfss": "2.未申诉",
    #                     "sdtr": "1.未发现",
    #                     "gkyyfzs": "1.未发现",
    #                     "cclxqk": "1.完整履行",
    #                     "ldgzqk": "2.足额",
    #                     "fieldcsqijjbb6": "精神状态",
    #                     "jszt": [
    #                         "1.衣着整洁"
    #                     ],
    #                     "field5a4vekffv": "交流沟通情况",
    #                     "thljx": "2.逻辑性一般",
    #                     "byjcht": "2.无",
    #                     "bebtht": "2.无",
    #                     "fyxl": "2.否",
    #                     "fielddhebuldks": "情绪状态",
    #                     "qxzt": [
    #                         "4.情绪无变化"
    #                     ],
    #                     "fieldbi2k87ajcz": "睡眠状态",
    #                     "smzt": [
    #                         "6.正常"
    #                     ],
    #                     "fieldnau9vqj27": "生活作息规律",
    #                     "shzxgl": "1.正常",
    #                     "fieldi5bawtnf7a": "躯体表现",
    #                     "qtbx": [
    #                         "5.正常"
    #                     ],
    #                     "fieldslzmn5vbs": "狱内再犯罪",
    #                     "ynzfz": "2.否",
    #                     "fieldfmjj9aovs": "其他法律问题",
    #                     "sfbh": [
    #                         "6.否"
    #                     ],
    #                     "fieldmqbc4liazm": "观察到的其他情况 ",
    #                     "qtqk": "无",
    #                     "field6y9qvmmf2e": 31,
    #                     "criminalIdentityField": "user"
    #                 },
    #                 "formId": process_info['formId'],
    #                 "updateTime": ""
    #             }
    #         except Exception as e:
    #             huixin_app.logger.error(f"生成【罪犯行为观察表】数据失败: {str(e)}")
    #             raise AssertionError(f"【罪犯行为观察表】数据生成失败: {str(e)}")
    #
    #     return data_generator

    # ------------------------------
    # 个体危险审批表
    # ------------------------------
    @staticmethod
    def build_criminal_gtwx_audit_lb(huixin_app: HuiXin, suicide_level='低', violent_level='低', escape_level='低',
                                     danger_level='低', ):
        """构建个体危险性审批量表的数据"""

        def data_generator():
            try:
                # 获取流程信息和罪犯基本信息
                huixin_app.logger.debug("===== 开始执行 data_generator 生成数据 =====")
                process_info = huixin_app.police_get_current_process_information(
                    processNode=ProcessNode.罪犯行为观察表
                )
                criminal_info = huixin_app.criminal_information['baseinfo']
                return {
                    "data": {
                        "pusherField": process_info['data']['pusherField'],
                        "crimeNameField": criminal_info.get('crimeName', ""),
                        "crimeIdField": [
                            criminal_info.get('id', "")
                        ],
                        "instanceField": process_info.get('flowInstanceId', ""),
                        "crimeid": criminal_info.get('id', ""),
                        "crimename": criminal_info.get('name', ""),
                        "presonarea": criminal_info.get('preson_area', ""),
                        'policeopinion': '',
                        "suicide_tendency": [
                            "极高"
                        ],
                        "violent_tendency": [
                            "中"
                        ],
                        "escape_tendency": [
                            "中"
                        ],
                        "danger_level": [
                            "极高"
                        ],
                        "scale_risk_factors": "暴力风险极高;\n自杀风险高;\n脱逃风险高;\n此人性格较为冲动、易怒。时常倾向使用暴力应对冲突;\n此人不适应狱内改造生活。对于改造任务，管教方式有一定情绪。自我感受压抑，焦虑，烦躁;\n此人有自责，抑郁倾向较为严重；有或曾有过实施自伤，自杀的想法;\n此人缺乏来自家庭、朋友的关怀，与同改关系紧张;\n",
                        "act_observ_danger_level": "低",
                        "negative_event_impact_level": "无",
                        "evaluation_reason": "评估中心/相关科室提出观察需求",
                        "reason_describe": "原因",
                        "now_suicide_tendency": [
                            suicide_level
                        ],
                        "now_violent_tendency": [
                            violent_level
                        ],
                        "now_escape_tendency": [
                            escape_level
                        ],
                        "now_danger_level": [
                            danger_level
                        ],
                        "finishing_people": process_info.get('creatorName', ""),
                        "criminalIdentityField": "user"
                    },
                }
            except Exception as e:
                huixin_app.logger.error(f"生成【个体危险审批表】数据失败: {str(e)}")
                raise AssertionError(f"【个体危险审批表】数据生成失败: {str(e)}")

        return data_generator

    def create_criminal_healthy_data(self):
        """生成【罪犯健康状况表】数据"""
        """构建个体危险性审批量表的数据"""

        def data_generator():
            try:
                # 获取流程信息和罪犯基本信息
                # 获取流程信息和罪犯基本信息
                # 获取流程信息
                self.huixin_server.logger.debug("===== 开始执行 data_generator 生成数据 =====")
                id, task_info = self.huixin_server.criminal_pre_sheet_submit_info('身心健康评估量表')
                criminal_info = self.huixin_server.criminal_information['baseinfo']
                data = {
                    'afpTaskId': id,
                    "data": {
                        "crimePusherField": task_info['data']['crimePusherField'],
                        "crimeNameField": task_info['data']['crimeNameField'],
                        "packageInstanceId": task_info['data']['packageInstanceId'],
                        "crimeIdField": task_info['data']['crimeIdField'],
                        "instanceField": task_info['data']['instanceField'],

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
                        "crimename": criminal_info['name'],
                        "crimeid": criminal_info['id'],
                        "an13": criminal_info['age'].replace('岁', ''),
                        "presonarea": criminal_info['preson_area'],
                        "timu1_1": "1",
                        "timu1_2": "0",
                        "timu1_3": "1",
                        "timu1_4": "0",
                        "timu1_5": "0",
                        "timu1_6": "0",
                        "timu1_7": "0",
                        "timu1_8": "0",
                        "timu1_9": "0",
                        "timu1_10": "0",
                        "timu1_11": "0",
                        "timu1_12": "0",
                        "timu1_13": "0",
                        "timu1_14": "0",
                        "timu1_15": "0",
                        "timu1_16": "0",
                        "timu1_17": "0",
                        "timu1_18": "0",
                        "timu1_19": "0",
                        "timu1_20": "0",
                        "timu1_21": "0",
                        "timu1_22": "0",
                        "timu1_23": "0",
                        "timu1_24": "0",
                        "timu1_25": "0",
                        "timu1_26": "0",
                        "timu1_27": "1",
                        "timu1_28": "0",
                        "timu1_29": "0",
                        "timu1_30": "0",
                        "timu1_31": "0",
                        "timu1_32": "1",
                        "timu1_33": "1",
                        "timu1_34": "1",
                        "timu1_35": "1",
                        "timu1_36": "1",
                        "timu1_37": "1",
                        "timu1_38": "0",
                        "timu1_39": "1",
                        "timu1_40": "0",
                        "timu1_41": "0",
                        "timu1_42": "0",
                        "timu1_43": "0",
                        "timu1_44": "1",
                        "timu1_45": "1",
                        "timu1_46": "0",
                        "timu1_47": "0",
                        "timu1_48": "1",
                        "timu1_49": "0",
                        "timu1_50": "1",
                        "timu1_51": "1",
                        "timu1_52": "0",
                        "timu1_53": "0",
                        "timu1_54": "0",
                        "timu1_55": "0",
                        "timu1_56": "0",
                        "timu1_57_1": "1",
                        "timu1_57_2": "1",
                        "timu1_57_3": "0",
                        "timu1_57_4": "0",
                        "timu1_57_5": "0",
                        "timu1_57_6": "1",
                        "timu1_58_1": "0",
                        "timu1_58_2": "1",
                        "timu1_58_3": "1",
                        "timu1_58_4": "1",
                        "timu1_58_5": "0",
                        "timu1_58_6": "0",
                        "timu1_58_7": "0",
                        "timu1_58_8": "0",
                        "timu1_58_9": "0",
                        "timu1_58_10": "0",
                        "timu1_58_11": "1",
                        "timu1_58_12": "0",
                        "timu1_58_13": "1",
                        "timu1_58_14": "1",
                        "timu1_58_15": "0",
                        "timu2_1": "0",
                        "timu2_2": "1",
                        "timu2_3": "1",
                        "timu2_4": "1",
                        "timu2_5": "1",
                        "timu2_6": "0",
                        "timu2_7": "1",
                        "timu2_8": "0",
                        "timu2_9": "0",
                        "timu2_10": "0",
                        "timu2_11": "1",
                        "timu3_1": "2",
                        "timu3_2": "2",
                        "timu3_3": "3",
                        "timu3_4": "1",
                        "timu3_5": "4",
                        "timu3_6": "2",
                        "timu3_7": "3",
                        "timu3_8": "1",
                        "timu4_1": "4",
                        "timu4_2": "3",
                        "timu4_3": "2",
                        "timu4_4": "2",
                        "timu4_5": "2",
                        "timu5_1": "1",
                        "timu5_2": "3",
                        "timu5_3": "3",
                        "timu5_4": "2",
                        "timu5_5": "2",
                        "timu6_1": "4",
                        "timu6_2": "3",
                        "timu6_3": "3",
                        "timu6_4": "2",
                        "timu6_5": "2",
                        "timu6_6": "3",
                        "timu6_7": "3",
                        "timu6_8": "3",
                        "timu6_9": "2",
                        "timu6_10": "2",
                        "timu6_11": "2",
                        "timu6_12": "4",
                        "timu6_13": "2",
                        "timu6_14": "3",
                        "timu6_15": "2",
                        "timu6_16": "2",
                        "timu6_17": "2",
                        "timu6_18": "2",
                        "timu6_19": "4",
                        "timu6_20": "3",
                        "timu6_21": "2",
                        "timu6_22": "2",
                        "timu6_23": "2",
                        "timu6_24": "2",
                        "timu6_25": "5",
                        "timu6_26": "3",
                        "timu6_27": "3",
                        "timu6_28": "3",
                        "timu6_29": "2",
                        "timu6_30": "2",
                        "timu6_31": "2",
                        "timu6_32": "2",
                        "timu6_33": "3",
                        "timu7_1": "0",
                        "timu7_2": "0",
                        "timu7_3": "0",
                        "timu7_4": "0",
                        "timu7_5": "0",
                        "timu7_6": "1",
                        "timu7_7": "0",
                        "timu7_8": "0",
                        "timu7_9": "1",
                        "timu7_10": "0",
                        "timu7_11": "0",
                        "timu7_12": "1",
                        "timu7_13": "0",
                        "timu7_14": "0",
                        "timu7_15": "0",
                        "timu7_16": "1",
                        "timu7_17": "1",
                        "timu7_18": "1",
                        "timu7_19": "0",
                        "timu7_20": "0",
                        "timu7_21": "0",
                        "timu7_22": "1",
                        "timu7_23": "0",
                        "timu7_24": "0",
                        "timu7_25": "0",
                        "timu7_26": "0",
                        "timu7_27": "1",
                        "timu7_28": "1",
                        "timu7_29": "0",
                        "timu7_30": "0",
                        "timu7_31": "0",
                        "timu7_32": "0",
                        "timu7_33": "1",
                        "timu7_34": "0",
                        "timu7_35": "0",
                        "timu7_36": "0",
                        "timu7_37": "0",
                        "timu7_38": "0",
                        "timu7_39": "0",
                        "timu7_40": "1",
                        "timu8_1": "2",
                        "timu8_2": "2",
                        "timu8_3": "2",
                        "timu8_4": "2",
                        "timu8_5": "2",
                        "timu8_6": "3",
                        "timu8_7": "2",
                        "timu8_8": "2",
                        "timu8_9": "2",
                        "timu8_10": "2",
                        "timu8_11": "3",
                        "timu8_12": "4",
                        "timu8_13": "3",
                        "timu8_14": "3",
                        "timu8_15": "5",
                        "timu8_16": "5",
                        "timu8_17": "2",
                        "timu8_18": "3",
                        "timu8_19": "2",
                        "timu8_20": "2",
                        "timu8_21": "2",
                        "timu9_1": "2",
                        "timu9_2": "2",
                        "timu9_3": "3",
                        "timu10_1": "2",
                        "timu10_2": "2",
                        "timu10_3": "3",
                        "timu10_4": "2",
                        "timu10_5": "2",
                        "timu10_6": "2",
                        "timu10_7": "2",
                        "timu11_1": "2",
                        "timu11_2": "2",
                        "fieldzc478x4lbj": 84,
                        "criminalIdentityField": "criminal",
                        "pusherField": [
                            "admin"
                        ]
                    },
                    "formId": task_info['formId'],
                    "updateTime": ""
                }
                return data
            except Exception as e:
                self.huixin_server.logger.error(f"生成【身心健康评估量表】数据失败: {str(e)}")
                raise AssertionError(f"【身心健康评估量表】数据生成失败: {str(e)}")

        return data_generator

    def create_retrofitting_difficultly_data(self):
        """生成【罪犯健康状况表】数据"""
        """改造难易-中期问卷"""

        def data_generator():
            try:
                # 获取流程信息和罪犯基本信息
                # 获取流程信息和罪犯基本信息
                # 获取流程信息
                self.huixin_server.logger.debug("===== 开始执行 data_generator 生成数据 =====")
                id, task_info = self.huixin_server.criminal_pre_sheet_submit_info('改造难易-中期问卷')
                criminal_info = self.huixin_server.criminal_information['baseinfo']
                data = {
                    'afpTaskId': id,
                    'data': {
                        "crimePusherField": task_info['data']['crimePusherField'],
                        "crimeNameField": task_info['data']['crimeNameField'],
                        "packageInstanceId": task_info['data']['packageInstanceId'],
                        "crimeIdField": task_info['data']['crimeIdField'],
                        "instanceField": task_info['data']['instanceField'],

                        "fieldr65zqmirsm": "<p><span class=\"ql-size-large\">您好！您的刑期已过半，为帮助您更好的完成接下来的改造，我们希望了解您的近期情况，请按照您的实际情况认真在答题卷上做出真实可信的回答，全部回答后点击提交。如果您在填写过程中遇到困难，请向民警寻求帮助。</span></p>",
                        "crimeid": criminal_info['id'],
                        "crimename": criminal_info['name'],
                        "presonarea": criminal_info['preson_area'],
                        "an102": "2",
                        "an103": "1",
                        "an104": "1",
                        "an105": "1",
                        "an106": "1",
                        "an107": "1",
                        "an108": "1",
                        "an109": "1",
                        "an1010": "1",
                        "an1011": "1",
                        "an1012": "1",
                        "an1013": "2",
                        "an1014": "3",
                        "an1015": "3",
                        "an1016": "3",
                        "an38": "0",
                        "an314": "1",
                        "an323": "1",
                        "an31": "0",
                        "an310": "0",
                        "an35": "0",
                        "an312": "1",
                        "an99": "1",
                        "an911": "2",
                        "an912": "2",
                        "an94": "2",
                        "an1021": "2",
                        "an1024": "2",
                        "an1020": [
                            "6",
                            "5"
                        ],
                        "fieldy7tixfou4y": 18,
                        "criminalIdentityField": "criminal",
                        "pusherField": [
                            "admin"
                        ]
                    },
                    "formId": task_info['formId'],
                    "updateTime": ""
                }
                return data
            except Exception as e:
                self.huixin_server.logger.error(f"生成【改造难易-中期问卷】数据失败: {str(e)}")
                raise AssertionError(f"【改造难易-中期问卷】数据生成失败: {str(e)}")

        return data_generator

    def create_police_interview_data(self):
        """
        创建访谈辅助问卷数据
        :return: 包含访谈辅助问卷数据的字典
        """

        def data_generator():
            try:
                self.huixin_server.logger.debug("===== 开始执行 data_generator 生成数据 =====")

                process_info = self.huixin_server.current_process_information['currentNode']

                criminal_info = self.huixin_server.criminal_information['baseinfo']
                data = {
                    "data": {
                        "crimeNameField": criminal_info['name'],
                        "pusherField": process_info['afpTaskDetail']['data']['pusherField'],
                        "packageInstanceId": process_info['afpTaskDetail']['data']['packageInstanceId'],
                        "crimeIdField": [criminal_info['id']],
                        "instanceField": process_info['afpTaskDetail']['data']['instanceField'],
                        "crimeid": criminal_info['id'],
                        "crimename": criminal_info['name'],
                        "field5fswrlpcu2": "<p><span class=\"ql-size-large\">让罪犯讲一下如果给他一个道歉的机会，他想说些啥</span></p>",
                        "fieldxorq346xbi": "<p><span class=\"ql-size-large\">让罪犯</span><strong class=\"ql-size-large\">尽可能详细讲一下</strong><span class=\"ql-size-large\">本次犯罪对</span><strong class=\"ql-size-large\">被害人和被害人家属</strong><span class=\"ql-size-large\">造成的影响</span></p>",
                        "fieldx3rug85up9": "<p><span class=\"ql-size-large\">让罪犯复述被害人的姓名、年龄、身份（被害人是做什么的）</span></p>",
                        "presonarea": criminal_info['preson_area'],
                        "subject_selection": "第二套题",
                        "fieldpepazum047": [
                            {
                                "path": "/app-factory-web/s3/sobey/477056029060960256/de45efbb-2eeb-415c-96d3-3418facfb169.xlsx",
                                "name": "话题二：罪犯对被害人的认识（只有当罪犯本次犯罪中存在明确被害人时使用）.xlsx",
                                "needCopy": True
                            }
                        ],
                        "fieldqprin413t0": "二、罪犯对被害人的认识",
                        "fieldlu3yw0bcgl": "1.被害人身份",
                        "victim_identity_question1": [
                            "C.正确回答年龄",
                            "D.正确回答身份",
                            "B.正确回答姓名"
                        ],
                        "victim_identity_remark": "暂无内容",
                        "victim_identity_record": "自动化测试-记录",
                        "fieldz934jfzqdj": "2.对被害人及被害人家属造成的影响",
                        "impact_for_family_question1": [
                            "C.对被害人的经济损害",
                            "D.对被害人的情感伤害",
                            "E.对被害人家属的经济损害",
                            "F.对被害人家属的情感伤害",
                            "B.对被害人的生命危害"
                        ],
                        "impact_for_family_record": "自动化测试-记录",
                        "fieldm5n6w9n8vk": "3.道歉",
                        "apology_question1": [
                            "B.该作出赔偿",
                            "D.自己应该负责",
                            "E.将来避免做出类似行为"
                        ],
                        "apology_record": "自动化测试-记录",
                        "criminalIdentityField": "user"
                    },
                    "formId": process_info['afpTaskDetail']['formId'],
                    "updateTime": ""
                }
            except Exception as e:
                self.huixin_server.logger.error(f"生成【访谈辅助问卷】数据失败: {str(e)}")
                raise AssertionError(f"【访谈辅助问卷】数据生成失败: {str(e)}")
            return data

        return data_generator


# 个体危险性量表数据构建函数
def build_criminal_gtwx_lb(huixin_app: HuiXin) -> dict:
    """
    构建个体危险性量表的数据

    :param huixin_app: HuiXin 类的实例，用于获取相关信息
    :return: 包含个体危险性量表数据的字典
    """
    try:
        current_process_info = huixin_app.criminal_task_query_v2()['resultList'][0]
    except (KeyError, IndexError):
        current_process_info = {}

    data = {
        "data": {
            "crimePusherField": [
                current_process_info.get('crimeId', "")
            ],
            "crimeNameField": current_process_info.get('crimeName', ""),
            "crimeIdField": [
                current_process_info.get('crimeId', "")
            ],
            "instanceField": current_process_info.get('flowInstanceId', ""),
            "field83y57opff7": "<p><span class=\"ql-size-large\">这是一份对于服刑人员的心理健康状况以及监狱生活情况进行调查研究的问卷。主要目的为评估你在这里的心情状态，不会对你在这里的工作或者改造表现造成任何不良的影响。请你按照自身的真实情况来进行作答。所有题目都只能选择一个答案（单选），没有对错之分。请你按顺序依次作答，选择符合的选项，对于不确定的问题，只需要按照感觉选即可，不需要做过多的思考，请不要漏选。</span></p>",
            "crimeid": current_process_info.get('crimeId', ""),
            "crimename": current_process_info.get('crimeName', ""),
            "presonarea": current_process_info.get('prisonArea', ""),
            "question001": "2",
            "question002": "3",
            # 其他问题字段...
        },
        "formId": "",
    }
    return data


def middle_retrofitting_difficultly_table(huixin_app: HuiXin):
    try:
        process_list = huixin_app.criminal_task_query_v2()['resultList'][0]['taskVOS']
        process_info = {}
        for process in process_list:
            if process['cbStepName'] == '改造难易-中期问卷':
                process_info = process
        criminal_process = huixin_app.criminal_sheet_task(process_info['afpTaskId'])
        data = {
            'id': process_info['afpTaskId'],
            "data": {
                "crimePusherField": criminal_process['data']['crimePusherField'],
                "crimeNameField": criminal_process['data']['crimeNameField'],
                "packageInstanceId": criminal_process['data']['packageInstanceId'],
                "crimeIdField": criminal_process['data']['crimeIdField'],
                "instanceField": criminal_process['data']['instanceField'],
                "fieldn1yvmzzs3f": "<p><span class=\"ql-size-large\">您好！为有利于您更好地改造，我们希望了解您的个人特点及成长经历，请按照您的实际情况认真在答题卷上做出真实可信的回答，全部回答后点击提交。如果您在填写过程中遇到困难，请向民警寻求帮助。</span></p>",
                "crimeid": criminal_process['data']['crimeIdField'][0],
                "crimename": criminal_process['data']['crimeNameField'],
                "presonarea": huixin_app.criminal_information['baseinfo']['preson_area'],
                "fieldr65zqmirsm": "<p><span class=\"ql-size-large\">您好！您的刑期已过半，为帮助您更好的完成接下来的改造，我们希望了解您的近期情况，请按照您的实际情况认真在答题卷上做出真实可信的回答，全部回答后点击提交。如果您在填写过程中遇到困难，请向民警寻求帮助。</span></p>",
                "an102": "2",
                "an103": "2",
                "an104": "2",
                "an105": "3",
                "an106": "2",
                "an107": "2",
                "an108": "3",
                "an109": "1",
                "an1010": "2",
                "an1011": "1",
                "an1012": "2",
                "an1013": "2",
                "an1014": "1",
                "an1015": "2",
                "an1016": "3",
                "an38": "0",
                "an314": "0",
                "an323": "1",
                "an31": "1",
                "an310": "0",
                "an35": "0",
                "an312": "0",
                "an99": "1",
                "an911": "2",
                "an912": "1",
                "an94": "2",
                "an1021": "1",
                "an1024": "4",
                "an1020": [
                    "3",
                    "2"
                ],
                "fieldy7tixfou4y": 134,
                "criminalIdentityField": "criminal",
                "pusherField": [
                    "admin"
                ]
            },
            "formId": criminal_process['formId'],
            "updateTime": ""
        }
        return data
    except Exception as e:
        huixin_app.logger.error(f'改造难易-中期问卷 获取失败: {e}')
        raise AssertionError(f'改造难易-中期问卷 获取失败: {e}')


def middle_body_heart_healthy_table(huixin_app: HuiXin):
    try:
        process_list = huixin_app.criminal_task_query_v2()['resultList'][0]['taskVOS']
        process_info = {}
        for process in process_list:
            if process['cbStepName'] == '身心健康评估量表':
                process_info = process
        criminal_process = huixin_app.criminal_sheet_task(process_info['afpTaskId'])
        data = {
            'id': process_info['afpTaskId'],
            "data": {
                "crimePusherField": criminal_process['data']['crimePusherField'],
                "crimeNameField": criminal_process['data']['crimeNameField'],
                "packageInstanceId": criminal_process['data']['packageInstanceId'],
                "crimeIdField": criminal_process['data']['crimeIdField'],
                "instanceField": criminal_process['data']['instanceField'],
                "crimeid": criminal_process['data']['crimeIdField'][0],
                "crimename": criminal_process['data']['crimeNameField'],
                "presonarea": huixin_app.criminal_information['baseinfo']['preson_area'],
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
                "timu1_58": "<p>58 .我小时候（15岁以前）干过以下某些事情</p>",
                "timu1_57": "<p>57 .我凭一时冲动干过一些以下的事情以至给我带来麻烦</p>",
                "field1kkxii2ju2": "<p><strong class=\"ql-size-large\">一、</strong><span class=\"ql-size-large\">以下题目是对你的一些描述，在回答问题时，想想在过去的几年里你主要的感觉，思想和行为。“是”的意思是此描述一般来说对你合适，“否”的意思是此描述一般来说对你不合适，</span><strong class=\"ql-size-large\">每题只选一个答案。</strong><span class=\"ql-size-large\">答案无对错之分，请如实作答。</span></p>",
                "fieldfzwmq0ocf8": "<p><span class=\"ql-size-large\">\t</span><span style=\"color: rgb(0, 0, 0);\" class=\"ql-size-large\">请认真阅读每道题目，按要求将答案填写到对应的答题卡上，其中注意力检测题请根据题目提示填写。</span><strong style=\"color: rgb(0, 0, 0);\" class=\"ql-size-large\">如实填写将有助于你的改造生涯，不认真做答将会重做。</strong></p>",
                "an13": "57",
                "timu1_1": "0",
                "timu1_2": "1",
                "timu1_3": "0",
                "timu1_4": "0",
                "timu1_5": "0",
                "timu1_6": "0",
                "timu1_7": "0",
                "timu1_8": "1",
                "timu1_9": "0",
                "timu1_10": "1",
                "timu1_11": "0",
                "timu1_12": "1",
                "timu1_13": "1",
                "timu1_14": "0",
                "timu1_15": "1",
                "timu1_16": "1",
                "timu1_17": "0",
                "timu1_18": "0",
                "timu1_19": "1",
                "timu1_20": "0",
                "timu1_21": "0",
                "timu1_22": "0",
                "timu1_23": "0",
                "timu1_24": "0",
                "timu1_25": "0",
                "timu1_26": "1",
                "timu1_27": "0",
                "timu1_28": "0",
                "timu1_29": "1",
                "timu1_30": "0",
                "timu1_31": "0",
                "timu1_32": "0",
                "timu1_33": "1",
                "timu1_34": "1",
                "timu1_35": "0",
                "timu1_36": "0",
                "timu1_37": "0",
                "timu1_38": "1",
                "timu1_39": "1",
                "timu1_40": "1",
                "timu1_41": "0",
                "timu1_42": "1",
                "timu1_43": "0",
                "timu1_44": "0",
                "timu1_45": "0",
                "timu1_46": "0",
                "timu1_47": "0",
                "timu1_48": "0",
                "timu1_49": "1",
                "timu1_50": "1",
                "timu1_51": "0",
                "timu1_52": "1",
                "timu1_53": "1",
                "timu1_54": "1",
                "timu1_55": "0",
                "timu1_56": "1",
                "timu1_57_1": "0",
                "timu1_57_2": "0",
                "timu1_57_3": "0",
                "timu1_57_4": "1",
                "timu1_57_5": "0",
                "timu1_57_6": "0",
                "timu1_58_1": "0",
                "timu1_58_2": "0",
                "timu1_58_3": "0",
                "timu1_58_4": "1",
                "timu1_58_5": "0",
                "timu1_58_6": "0",
                "timu1_58_7": "0",
                "timu1_58_8": "0",
                "timu1_58_9": "0",
                "timu1_58_10": "0",
                "timu1_58_11": "0",
                "timu1_58_12": "0",
                "timu1_58_13": "0",
                "timu1_58_14": "0",
                "timu1_58_15": "0",
                "timu2_1": "0",
                "timu2_2": "1",
                "timu2_3": "1",
                "timu2_4": "0",
                "timu2_5": "0",
                "timu2_6": "0",
                "timu2_7": "0",
                "timu2_8": "0",
                "timu2_9": "1",
                "timu2_10": "0",
                "timu2_11": "1",
                "timu3_1": "2",
                "timu3_2": "2",
                "timu3_3": "2",
                "timu3_4": "2",
                "timu3_5": "2",
                "timu3_6": "2",
                "timu3_7": "2",
                "timu3_8": "2",
                "timu4_1": "2",
                "timu4_2": "3",
                "timu4_3": "2",
                "timu4_4": "2",
                "timu4_5": "2",
                "timu5_1": "2",
                "timu5_2": "2",
                "timu5_3": "2",
                "timu5_4": "2",
                "timu5_5": "2",
                "timu6_1": "3",
                "timu6_2": "2",
                "timu6_3": "1",
                "timu6_4": "2",
                "timu6_5": "2",
                "timu6_6": "2",
                "timu6_7": "4",
                "timu6_8": "2",
                "timu6_9": "4",
                "timu6_10": "2",
                "timu6_11": "4",
                "timu6_12": "4",
                "timu6_13": "3",
                "timu6_14": "3",
                "timu6_15": "3",
                "timu6_16": "3",
                "timu6_17": "2",
                "timu6_18": "5",
                "timu6_19": "3",
                "timu6_20": "1",
                "timu6_21": "4",
                "timu6_22": "3",
                "timu6_23": "5",
                "timu6_24": "4",
                "timu6_25": "3",
                "timu6_26": "3",
                "timu6_27": "2",
                "timu6_28": "4",
                "timu6_29": "4",
                "timu6_30": "2",
                "timu6_31": "3",
                "timu6_32": "2",
                "timu6_33": "2",
                "timu7_1": "1",
                "timu7_2": "1",
                "timu7_3": "0",
                "timu7_4": "1",
                "timu7_5": "0",
                "timu7_6": "1",
                "timu7_7": "1",
                "timu7_8": "0",
                "timu7_9": "1",
                "timu7_10": "1",
                "timu7_11": "1",
                "timu7_12": "1",
                "timu7_13": "1",
                "timu7_14": "0",
                "timu7_15": "0",
                "timu7_16": "0",
                "timu7_17": "0",
                "timu7_18": "1",
                "timu7_19": "1",
                "timu7_20": "0",
                "timu7_21": "0",
                "timu7_22": "0",
                "timu7_23": "0",
                "timu7_24": "0",
                "timu7_25": "1",
                "timu7_26": "0",
                "timu7_27": "0",
                "timu7_28": "1",
                "timu7_29": "0",
                "timu7_30": "0",
                "timu7_31": "1",
                "timu7_32": "0",
                "timu7_33": "0",
                "timu7_34": "0",
                "timu7_35": "0",
                "timu7_36": "0",
                "timu7_37": "1",
                "timu7_38": "0",
                "timu7_39": "0",
                "timu7_40": "0",
                "timu8_1": "2",
                "timu8_2": "2",
                "timu8_3": "3",
                "timu8_4": "2",
                "timu8_5": "2",
                "timu8_6": "2",
                "timu8_7": "5",
                "timu8_8": "3",
                "timu8_9": "4",
                "timu8_10": "2",
                "timu8_11": "5",
                "timu8_12": "4",
                "timu8_13": "3",
                "timu8_14": "3",
                "timu8_15": "3",
                "timu8_16": "3",
                "timu8_17": "4",
                "timu8_18": "3",
                "timu8_19": "3",
                "timu8_20": "3",
                "timu8_21": "3",
                "timu9_1": "3",
                "timu9_2": "4",
                "timu9_3": "6",
                "timu10_1": "4",
                "timu10_2": "3",
                "timu10_3": "2",
                "timu10_4": "2",
                "timu10_5": "3",
                "timu10_6": "2",
                "timu10_7": "2",
                "timu11_1": "4",
                "timu11_2": "5",
                "fieldzc478x4lbj": 341,
                "criminalIdentityField": "criminal",
                "pusherField": [
                    "admin"
                ]
            },
            "formId": criminal_process['formId'],
            "updateTime": ""
        }
        return data
    except Exception as e:
        huixin_app.logger.error(f'中期身心健康量表 获取失败: {e}')
        raise AssertionError(f'中期身心健康量表 获取失败: {e}')


# 体检表
def middle_confession_reform_data(huixin_app: HuiXin, processNode: ProcessNode):
    time.sleep(2)
    process_info = huixin_app.police_get_current_process_information(processNode=processNode,
                                                                     user_type=HUIXIN_USER.prison_police)

    criminal_info = huixin_app.criminal_information['baseinfo']
    data = {
        "data": {
            "crimeNameField": criminal_info['name'],
            "pusherField": process_info['data']['pusherField'],
            "crimeIdField": [
                criminal_info['id']
            ],
            "instanceField": process_info['data']['instanceField'],
            "packageInstanceId": "1935991503539167233",

            "crimeid": criminal_info['id'],
            "crimename": criminal_info['name'],
            "presonarea": "七监区",
            "fieldtc9qni75qn": "维度类别条目确认",
            "fieldimjk4r8vhm": "类别一：监管改造表现",
            "jglbmrzf": 25,
            "jgtm1mrdf": "5",
            "jgtm2mrdf": "5",
            "jgtm3mrdf": "5",
            "jgtm4mrdf": "5",
            "jgtm5mrdf": "3",
            "jgtm6mrdf": "2",
            "field1uo6rt95z0": "类别二：教育和文化改造表现",
            "jylbmrzf": 20,
            "jytm1mrdf": "5",
            "jytm2mrdf": "5",
            "jytm3mrdf": "3",
            "jytm4mrdf": "3",
            "jytm5mrdf": "2",
            "jytm6mrdf": "2",
            "fielda2uec6glpv": "类别三：劳动改造表现",
            "ldlbmrzf": 15,
            "ldtm1mrdf": "4",
            "ldtm2mrdf": "4",
            "ldtm3mrdf": "4",
            "ldtm4mrdf": "3",
            "field0k7jwxyg43": "类别四：财产性判项履行",
            "cctm2mrdf_reason": [
                "由后台计算得出"
            ],
            "cctm3mrdf_reason": [
                "由后台计算得出"
            ],
            "cctm4mrdf_reason": [
                "由后台计算得出"
            ],
            "cctm5mrdf_reason": [
                "由后台计算得出"
            ],
            "cclbmrzf": 10,
            "cctm1mrdf": "10",
            "field31r8u07ru6": "类别五：认罪悔罪",
            "rzhzlbmrzf": 27,
            "rzhz1mzdf": "5",
            "rzhz2mzdf": "5",
            "rzhz3mzdf": "5",
            "rzhz4mzdf": "4",
            "rzhz5mzdf": "4",
            "rzhz6mzdf": "4",
            "rzhz7mzdf": "0.0",
            "criminalIdentityField": "user"
        },
        "formId": "477431111759368192",
        "updateTime": "2025-06-20 17:22:00"
    }

    data = {
        "data": {
            "crimeNameField": criminal_info['name'],
            "pusherField": process_info['data']['pusherField'],
            "crimeIdField": [
                criminal_info['id']
            ],
            "instanceField": process_info['data']['instanceField'],
            "fieldovigp4aztf": "基本信息",
            "base_info": {
                "name": criminal_info['name'],
                "crime_num": criminal_info['id'],
                "sex": criminal_info['sex'],
                "national": criminal_info['nation'],
                "birth_date": criminal_info['birthday'],
                "hf": "是",
                "szjq": criminal_info['preson_area'],
                "zm": criminal_info['crime_name'],
                "xz": criminal_info['xq'],
                "xq": criminal_info['xq'],
                "fieldxuq10tn8a9": "妇科",
                "fk_wy": "无异常",
                "fk_yd": "无异常",
                "fk_gj": "无异常",
                "fk_gt": "无异常",
                "fk_fj": "无异常",
                "fk_qt": "无异常"
            },
            "sex": criminal_info['sex'],
            "fieldzdf7gz7ob2": "既往病史",
            "jwbs_sss": "无",
            "jwbs_gms": "无",
            "jwbs_wss": "无",
            "jwbs_jwyzdbs": "无",
            "jwbs_ztcj": "无",
            "field98d50oanww": "既往其他情况",
            "jwqt_xys": "无",
            "jwqt_yjs": "无",
            "jwqt_xds": "无",
            "fieldtaeyc906vq": "一般状态",
            "ybzt_sg": 180,
            "ybzt_tz": 150,
            "ybzt_xx": [
                "A"
            ],
            "ybzt_tw": 37,
            "ybzt_xy": [
                {
                    "shousuoya": 40,
                    "shuzhangya": 300
                }
            ],
            "field3ac8v8j3mx": "内科",
            "nk_xz": [
                {
                    "nk_xzxl": 100,
                    "nk_xzxlbq": [
                        "齐"
                    ],
                    "nk_xzzy": [
                        "无"
                    ]
                }
            ],
            "nk_gz": "无异常",
            "nk_fb": "无异常",
            "nk_pz": "无异常",
            "nk_shzh": "无异常",
            "nk_qt": "无异常",
            "fieldfw91iz7bd7": "外科",
            "wk_pf": "无异常",
            "wk_qblbj": "无异常",
            "wk_jzx": "无异常",
            "wk_rf": "无异常",
            "wk_jz": "无异常",
            "wk_sz": "无异常",
            "wk_gmzc": "无异常",
            "wk_wszq": "有异常",
            "wk_wszqyc": "生殖异常",
            "wk_qlxwkyc": "无异常",
            "wk_qt": "无异常",
            "fieldo56aqry0b1": "五官科",
            "fielduvevikc2jx": "30.眼",
            "wgk_lyslz": [
                "1.0"
            ],
            "wgk_lysly": [
                "1.0"
            ],
            "wgk_sj": "无异常",
            "wgk_wy": "无异常",
            "wgk_sm": "否",
            "wgk_kq": "无异常",
            "wgk_er": "无异常",
            "wgk_bi": "无异常",
            "wgk_hou": "无异常",
            "wgk_qt": "无异常",
            "fieldg7b9u0lgeo": "辅助检查",
            "fzjc_xcg": "血常规辅助",
            "fzjc_ncg": "尿常规辅助",
            "fzjc_szgn": "肝功能辅助",
            "fzjc_xdt": "心电图常规",
            "fzjc_csjc": "超声检查辅助",
            "fzjc_qt": "其他",
            "field18lrywzm5d": "放射科检查",
            "fskjc_xct": "无异常",
            "fskjc_qt": "无异常",
            "fieldct27hpyef5": "入监必检项目",
            "rjbj_fjhsc": "无异常",
            "rjbj_hivsc": "无异常",
            "rjbj_ygbmky": "无异常",
            "rjbj_mdlxtkt": "无异常",
            "fieldz956t7rahj": "其他项目",
            "qt_qtxm": "无异常",
            "fieldpp43e3xd3o": "自动化测试--主治医师意见",
            "zzysyj": "自动化测试--主治医师意见",
            "fieldstmx54pijs": "自动化测试--医院意见",
            "yiyuanyijian": "自动化测试--医院意见",
            "criminalIdentityField": "user"
        },
        "formId": process_info['formId'],
        "updateTime": ""
    }
    return data
