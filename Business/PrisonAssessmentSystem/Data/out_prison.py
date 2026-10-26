from Business.PrisonAssessmentSystem.API import HuiXin
from Business.PrisonAssessmentSystem.Data import *


def out_police_social_table(huixin_app: HuiXin, processNode: ProcessNode):
    """
    社会适应性
    :param processNode:
    :param huixin_app:
    :return:
    """
    process_info = huixin_app.police_get_current_process_information(processNode=processNode,
                                                                     user_type=HUIXIN_USER.prison_police)

    criminal_info = huixin_app.criminal_information['baseinfo']
    # 社会适应性
    data = {
        "data": {
            "crimeNameField": criminal_info['name'],
            "pusherField": process_info['data']['pusherField'],
            "crimeIdField": [
                criminal_info['id']
            ],
            "instanceField": process_info['data']['instanceField'],
            "packageInstanceId": process_info['data']['packageInstanceId'],
            "fieldx0htj93wju": "<p><span class=\"ql-size-large\">需要作为社会适应模型的前置问卷，请您结合当前服刑人员的罪犯情况进行填写。</span></p>",
            "crimeid": criminal_info['id'],
            "crimename": criminal_info['name'],

            "presonarea": criminal_info['preson_area'],
            "shsyxtptm2": "否",
            "shsyxtptm3": "社会支持充足",
            "criminalIdentityField": "user"
        },
        "formId": process_info['formId'],
        "updateTime": ""
    }
    return data


# 【罪犯填写】社会适应性评估量表
def out_criminal_social_table(huixin_app: HuiXin):
    """
    :param huixin_app:
    :return:
    """
    try:
        process_list = huixin_app.criminal_task_query_v2()['resultList'][0]['taskVOS']
        process_info = {}
        for process in process_list:
            if process['cbStepName'] == '社会适应性评估量表':
                process_info = process
        criminal_process = huixin_app.criminal_sheet_task(process_info['afpTaskId'])
        data = {
            'id': process_info['afpTaskId'],
            "data": {
                "crimeIdField": criminal_process['data']['crimeIdField'],
                "crimeNameField": criminal_process['data']['crimeNameField'],
                "crimePusherField": criminal_process['data']['crimePusherField'],
                "crimeid": criminal_process['data']['crimeIdField'][0],
                "crimename": criminal_process['data']['crimeNameField'],
                'crimesex': [huixin_app.criminal_information['baseinfo']['sex']],
                "packageInstanceId": criminal_process['data']['packageInstanceId'],
                "instanceField": criminal_process['data']['instanceField'],
                "presonarea": huixin_app.criminal_information['baseinfo']['preson_area'],
                "fieldh7ioe46e78": "<p><strong class=\"ql-size-large\" style=\"color: rgb(0, 102, 204);\">0 代表该句话完全不符合您的情况；1&nbsp;代表不太符合您的情况；2 代表基本符合您的情况； 3 代表大部分符合您的情况；4&nbsp;代表完全符合您的情况</strong></p>",
                "fieldjl8n7udqr2": "<p><span class=\"ql-size-large\">﻿下面是一些个人对自己的看法的陈述。填答时，请您看清楚每句话的意思，然后勾选一 个数字，以代表该句话与您现在对自己的看法相符合的程度。每个人对自己的看法都有其独 特性。因此答案是没有对错的，您只要如实回答就可以了。</span></p>",
                "shsyxlmtm1": "2 基本符合",
                "shsyxlmtm2": "2 基本符合",
                "shsyxlmtm3": "3 大部分符合",
                "shsyxlmtm4": "2 基本符合",
                "shsyxlmtm5": "3 大部分符合",
                "shsyxlmtm6": "2 基本符合",
                "shsyxlmtm7": "3 大部分符合",
                "shsyxlmtm8": "2 基本符合",
                "shsyxlmtm9": "2 基本符合",
                "shsyxlmtm10": "3 大部分符合",
                "shsyxlmtm11": "2 基本符合",
                "shsyxlmtm12": "2 基本符合",
                "shsyxlmtm13": "2 基本符合",
                "shsyxlmtm14": "2 基本符合",
                "shsyxlmtm15": "3 大部分符合",
                "shsyxlmtm16": "3 大部分符合",
                "shsyxlmtm17": "2 基本符合",
                "shsyxlmtm18": "3 大部分符合",
                "shsyxlmtm19": "2 基本符合",
                "shsyxlmtm20": "4 完全符合",
                "shsyxlmtm21": "4 完全符合",
                "shsyxlmtm22": "4 完全符合",
                "shsyxlmtm23": "4 完全符合",
                "shsyxlmtm24": "4 完全符合",
                "shsyxlmtm25": "4 完全符合",
                "shsyxlmtm26": "4 完全符合",
                "shsyxlmtm27": "4 完全符合",
                "shsyxlmtm28": "4 完全符合",
                "shsyxlmtm29": "4 完全符合",
                "fieldvnxge22npg": 52,
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
        huixin_app.logger.error(f'社会适应性评估量表 获取失败: {e}')
        raise AssertionError(f'社会适应性评估量表 获取失败: {e}')


# 【罪犯填写】社会适应性调查出监问卷
def out_criminal_social_table_02(huixin_app: HuiXin):
    """
    :param huixin_app:
    :return:
    """
    try:
        process_list = huixin_app.criminal_task_query_v2()['resultList'][0]['taskVOS']
        process_info = {}
        for process in process_list:
            if process['cbStepName'] == '社会适应性调查出监问卷':
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
                "fieldx650ii2uaq": "<p><span class=\"ql-size-large\">下面是一份关于服刑人员社会适应性的调查表，旨在收集相关信息用于科学研究，问题的答案没有对错好坏之分，不会对您的加扣分造成影响。请您放心作答，将符合自己实际情况的选项勾选，不要多选，也不要漏选。</span></p>",
                "xhyzk": "丧偶",
                "hybd": "无变动",
                "question034": "无",
                "question033": "无",
                "question030": [
                    "无"
                ],
                "question019": "是",
                "question011": "可能会",
                "question031": "无",
                "question028": "有计划",
                "question010": "缴纳，小于15年",
                "fieldo0q1nov420": 28,
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
        huixin_app.logger.error(f'社会适应性调查出监问卷 获取失败: {e}')
        raise AssertionError(f'社会适应性调查出监问卷 获取失败: {e}')


# 【罪犯填写】职业技能出监问卷
def out_criminal_skills_01(huixin_app: HuiXin):
    """
    :param huixin_app:
    :return:
    """
    try:
        process_list = huixin_app.criminal_task_query_v2()['resultList'][0]['taskVOS']
        process_info = {}
        for process in process_list:
            if process['cbStepName'] == '职业技能出监问卷':
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
                "fieldje7xneizxz": ["电脑"],
                'fieldkiqwrbxvuo': ["美容师资格证"],
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
        huixin_app.logger.error(f'职业技能出监问卷 获取失败: {e}')
        raise AssertionError(f'职业技能出监问卷 获取失败: {e}')
