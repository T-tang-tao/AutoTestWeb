import json
import time
from datetime import datetime

from Business.PrisonAssessmentSystem.API import HuiXin
from Business.PrisonAssessmentSystem.Data import ProcessNode, HUIXIN_USER
from Business.PrisonAssessmentSystem.Service import HuiXinService


class audit_DataFactory():
    """数据工厂类：统一管理所有测试数据的生成逻辑"""
    """表单提交数据工厂"""

    def __init__(self, huiXinService: HuiXinService):
        self.huixin_server = huiXinService
    # ------------------------------
    # 个体危险审批表
    # ------------------------------
    @staticmethod
    def audit_inmate_criminal_base_info(huixin_app: HuiXin):
        """生成【入监基本信息采集】数据"""
        def data_generator():
            try:
                # 查询审核流程
                auditProcess = huixin_app.police_audit_search(user_type=HUIXIN_USER.prison_police)
                id = auditProcess['resultList'][0]['id']

                data = {
                    'id': id,
                    'remark': '自动化审核',
                    "reportFileData": []
                }
                return data
            except Exception as e:
                huixin_app.logger.error(f"生成【入监基本信息采集】数据失败: {str(e)}")
                raise AssertionError(f"【入监基本信息采集】数据生成失败: {str(e)}")

        return data_generator

    @staticmethod
    def audit_mid_gtwx(huixin_app: HuiXin):
        """生成【入监基本信息采集】数据"""
        def data_generator():
            try:
                # 查询审核流程
                auditProcess = huixin_app.police_audit_search(user_type=HUIXIN_USER.prison_police)
                id = auditProcess['resultList'][0]['id']
                data = {
                    "reportFileData": [
                        {
                            "afpInstanceId": "1957272826101932032",
                            "reportId": "474641540107609861",
                            "fileObjectName": "history/1957272826101932032/@个体危险评估【报告】@1755486126458.docx",
                            "fileData": {
                                "id": "pg02008132",
                                "xq": "死刑缓期执行",
                                "yx": "8年4月29日",
                                "sex": "男",
                                "name": "",
                                "wushe": "涉毒",
                                "dqxqzr": "2034-01-16 00:00:00",
                                "dqxxqr": "2015-08-17 00:00:00",
                                "lbwxys": "中低度，暂不填写",
                                "nation": "汉族",
                                "period": "中期",
                                "crimelg": "否",
                                "xwgc_dj": "低",
                                "__extend": {
                                    "danger": "中",
                                    "period": "audit",
                                    "easyFlow": "否"
                                },
                                "birthday": "1975-07-24 00:00:00",
                                "isRuJian": false,
                                "measures": "scriptError:dangerMeasureCommend[0].measures",
                                "rj_break": "scriptError:risk_assessment[0].$BreakTendLevel",
                                "zq_break": "低",
                                "__DateNow": "2025-08-18 10:46:20",
                                "before_dj": "中",
                                "education": "本科及以上未毕业",
                                "isZhongQi": true,
                                "crime_name": "贩卖毒品",
                                "enter_data": "2011-11-10 00:00:00",
                                "fix_factor": "",
                                "rj_suicide": "scriptError:risk_assessment[0].$SuicideTendLevel",
                                "rj_violent": "scriptError:risk_assessment[0].$ViolentTendLevel",
                                "zq_suicide": "低",
                                "zq_violent": "低",
                                "penaldetail": null,
                                "preson_area": "一监区",
                                "risk_factor": "暴力解释因子：该罪犯家庭管教方式属于放任型，从小行为不受约束，可能会养成暴力行为；存在吸毒行为，容易因神经受损而导致控制力下降，发生攻击行为；有赌博欠下的债务，心理压力大，容易产生极端思想；\n自杀解释因子：该罪犯存在大额债务，无法偿还，可能因此产生自杀想法；担心家里老人没人照顾，内疚感强，可能产生自杀想法；担心家里子女没人照顾，内疚感强，可能产生自杀想法；担心子女的教育问题，内疚感强，易产生自杀想法；\n脱逃解释因子：该罪犯担心家里老人没人照顾，感到焦躁不安、自责感强，可能产生脱逃想法；担心家里子女没人照顾，感到焦躁不安、自责感强，可能产生脱逃想法；担心家人生活困难，感到内疚、自责，可能产生脱逃想法；\n",
                                "__PrisonName": "德阳监狱",
                                "isCustomFlow": true,
                                "isSimpleFlow": false,
                                "marriage_now": "已婚",
                                "native_place": "贵州省盘州市",
                                "simple_break": "scriptError:SimpleInfoQuery[0].break",
                                "middle_reason": "经教育、疏导后，该犯过激言行改善情况不佳",
                                "negativeevent": [],
                                "simple_danger": "scriptError:SimpleInfoQuery[0].danger",
                                "family_address": "贵州省盘州市马场乡业嘎村一组",
                                "needAssessment": true,
                                "simple_suicide": "scriptError:SimpleInfoQuery[0].suicide",
                                "simple_violent": "scriptError:SimpleInfoQuery[0].violent",
                                "break_tend_desc": "scriptError:risk_assessment[0].break_tend_desc",
                                "rj_danger_level": "scriptError:risk_assessment[0].$danger_level",
                                "zq_danger_level": "低",
                                "suicide_tend_desc": "scriptError:risk_assessment[0].suicide_tend_desc",
                                "violent_tend_desc": "scriptError:risk_assessment[0].violent_tend_desc",
                                "crime_record_count": "无",
                                "act_observ_danger_level": "低",
                                "reason": null,
                                "measure": null,
                                "review_violent": [
                                    "低"
                                ],
                                "review_break": [
                                    "低"
                                ],
                                "review_suicide": [
                                    "低"
                                ],
                                "review_danger_level": [
                                    "低"
                                ],
                                "policeopinion": "自动化",
                                "prisonopinion": null,
                                "assessmentcentreopinion": null,
                                "__auditInfo": {
                                    "主管民警": {
                                        "auditor": "陈秀",
                                        "date": "2025-08-18 11:03:33"
                                    }
                                }
                            },
                            "assessmentFlowInstanceId": "643a62f20a3a42aea1fdf1bf7ce0c48c"
                        }
                    ]
                }
                return data
            except Exception as e:
                huixin_app.logger.error(f"<UNK>: {str(e)}")
                raise e

        return data_generator

    # 个体危险审批表  民警
    def audit_gtwx(huixin_app: HuiXin):
        current_process_information = huixin_app.current_process_information
        criminal_information = huixin_app.criminal_information
        data = {
            "reportFileData": [
                {
                    "afpInstanceId": "1921853179311730688",
                    "reportId": "474641540107609861",
                    "fileObjectName": "history/1921853179311730688/@个体危险评估【报告】@1747040491419.docx",
                    "fileData": {
                        "id": "pg10071910",
                        "xq": "5年6月0日",
                        "yx": None,
                        "sex": "男",
                        "name": "达拉",
                        "wushe": "涉毒",
                        "dqxqzr": "2024-05-18 00:00:00",
                        "dqxxqr": "2018-11-19 00:00:00",
                        "lbwxys": "scriptError:reportXwgcDj[0].lbwxys",
                        "nation": "藏族",
                        "period": "入监",
                        "crimelg": "累犯",
                        "xwgc_dj": "scriptError:reportXwgcDj[0].xwgcDj",
                        "__extend": {
                            "easyFlow": "否"
                        },
                        "birthday": "1965-06-10 00:00:00",
                        "isRuJian": True,

                        "measures": [
                            "1.严格落实清人点名制度；",
                            "2.剖析自杀原因，开展专项矫正；",
                            "3.严格落实个别谈话制度；",
                            "4.严格禁止安排自由流动岗位；",
                            "5.严格落实“五专”管理和“六个”防范；",
                            "6.严格落实耳目暗控，信息员贴靠制度；",
                            "7.适时开展心理危机干预；",
                            "8.严格落实包夹监控，严防单独行动；",
                            "9.严格落实搜身及清监制度；",
                            "10.严格落实会见、亲情电话实时监听；",
                            "11.严格落实“一犯一策”教育转化方案；",
                            "12.严格实行“24小时”挂屏监控；",
                            "13.严格禁止接触危化品；",
                            "14.严格落实“三大现场”就近管控；",
                            "15.严格禁止进入高风险劳动区域；",
                            "16.严格禁止接触中、高风险工具；"
                        ],
                        "rj_break": "中",
                        "zq_break": "scriptError:middleRiisk[0].break",
                        "__DateNow": "2025-05-12 17:01:18",
                        "before_dj": "scriptError:middleRiisk[0].before_dj",
                        "education": "文盲（没读过书）",
                        "isZhongQi": False,
                        "crime_name": "受贿、私分国有资产",
                        "enter_data": "2019-09-04 00:00:00",
                        "fix_factor": "scriptError:middleRiisk[0].fix_factor",
                        "rj_suicide": "极高",
                        "rj_violent": "中",
                        "zq_suicide": "scriptError:middleRiisk[0].suicide",
                        "zq_violent": "scriptError:middleRiisk[0].violent",
                        "description": "scriptError:middleRiisk[0].description",
                        "penaldetail": None,
                        "preson_area": "十监区",
                        "risk_factor": "scriptError:middleRiisk[0].risk_factor",
                        "__PrisonName": "德阳监狱",
                        "isCustomFlow": True,
                        "isSimpleFlow": '1',
                        "marriage_now": "已婚",
                        "native_place": "四川省阿坝藏族羌族自治州若尔盖县",
                        "simple_break": "scriptError:SimpleInfoQuery[0].break",
                        "middle_reason": "scriptError:middleRiisk[0].reason",
                        "negativeevent": [],
                        "simple_danger": "scriptError:SimpleInfoQuery[0].danger",
                        "family_address": "四川省马尔康市马尔康镇高原影城17楼3号",
                        "simple_suicide": "scriptError:SimpleInfoQuery[0].suicide",
                        "simple_violent": "scriptError:SimpleInfoQuery[0].violent",
                        "break_tend_desc": "本次评估中该罪犯的脱逃等级为中度，但是存在曾当过警察，可能具有利于脱逃的技能;曾服过兵役，可能具有利于脱逃的技能;有攀爬技能，具备实施脱逃行为的条件的潜在危险因子，请注意结合现实改造表现综合研判。",
                        "rj_danger_level": "极高",
                        "zq_danger_level": "scriptError:middleRiisk?middleRiisk[0].dj : null",
                        "suicide_tend_desc": "本次评估中该罪犯的自杀等级为极高度，该罪犯具有强迫症状，会对自杀意念产生消极影响；易对一些事物或场所产生恐惧，是影响自杀行为的危险因素；心理灵活性较低，一旦形成自杀思想不易改变，同时罪犯存在家族精神病史，可能因精神病遗传而导致产生自杀想法;杀害/伤害亲人带来巨大的罪责感和愧疚心，思想压力大， 易产生自杀倾向;幼年曾被性侵，产生心理阴影，存在自杀可能性;幼年曾被猥亵，产生心理阴影，存在自杀可能性;有吸毒史，可能会因吸毒导致的精神异常问题，发生自杀行为。综合以上因素认为罪犯的自杀等级为极高。",
                        "violent_tend_desc": "本次评估中该罪犯的暴力等级为中度，但是存在曾当过警察，具有一定搏击格斗技能;曾服过兵役，具有一定搏击格斗技能;存在家族精神病史，因精神疾病导致的暴力行为可能性大;存在长期饮酒行为，容易降低自控能力，发生暴力行为;家庭管教方式属于放任型，从小行为不受约束，可能会养成暴力行为;存在吸毒行为，容易因神经受损而导致控制力下降，发生攻击行为;有赌博欠下的债务，心理压力大，容易产生极端思想的潜在危险因子，请注意结合现实改造表现综合研判。",
                        "crime_record_count": "无",
                        "act_observ_danger_level": "scriptError:middleRiisk[0].act_observ_danger_level",
                        "reason": null,
                        "measure": null,
                        "review_violent": [
                            "低"
                        ],
                        "review_break": [
                            "低"
                        ],
                        "review_suicide": [
                            "低"
                        ],
                        "review_danger_level": [
                            "低"
                        ],
                        "policeopinion": "test",
                        "prisonopinion": null,
                        "assessmentcentreopinion": null,
                        "__auditInfo": {
                            "主管民警": {
                                "auditor": Users[''],
                                "date": "2025-05-12 17:02:17"
                            }
                        }
                    },
                    "assessmentFlowInstanceId": "82562fcae189437c9ca114bd4752c895"
                }
            ]
        }


audit_user = {}


# 审核 监区领导
def audit_gtwx_table(huixin_app: HuiXin, user_type: HUIXIN_USER, escape_level='低', violent_level='低',
                     suicide_level='低', danger_level='低'):
    """

    :param huixin_app:
    :param user_type:
    :param danger_level: 取其他三个等级最高
    :param escape_level: 逃逸等级
    :param violent_level: 暴力等级
    :param suicide_level: 自杀等级
    :return:
    """
    # 查询审核流程
    auditProcess = huixin_app.police_audit_search(user_type=user_type)
    id = auditProcess['resultList'][0]['id']

    ppId = auditProcess['resultList'][0]['ppId']
    # 获取sourceId
    content = huixin_app.police_audit_report_content(id=id)
    sourceId = content[0]['sourceId']

    # 获取tblReportId
    reportResult = huixin_app.police_report_result(id=sourceId)
    reportResultId = reportResult['content']['id']
    tblReportId = reportResult['content']['tblReportId']

    # 获取report
    reportDetail = huixin_app.police_audit_report_detail(
        tblReportId=tblReportId)

    fileName = reportResult['content']['name']
    afpInstanceId = reportResult['content']['afpInstanceId']
    assessmentFlowInstanceId = reportResult['content']['flowInstanceId']
    executeResult = json.loads(reportResult['content']['executeResult'])

    executeResult['review_break'] = [escape_level]
    executeResult['review_violent'] = [violent_level]
    executeResult['review_suicide'] = [suicide_level]
    executeResult['review_danger_level'] = [danger_level]
    # 民警审核
    executeResult['policeopinion'] = '自动化-测试-主管民警-意见'
    # 监狱领导审核
    executeResult['prisonopinion'] = '自动化-测试-监狱领导-意见'
    # 评估中心意见
    executeResult['assessmentcentreopinion'] = '自动化-测试-评估中心-意见'

    fileObjectName = f"history/{afpInstanceId}/@{fileName}@{int(time.time() * 1000)}.docx"

    audit_user[huixin_app.current_user.value] = {

        "auditor": huixin_app.users[huixin_app.current_user.name]['name'],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

    }
    executeResult['__auditInfo'] = audit_user

    data = {
        'id': id,
        'audit_data': {"reportFileData": [
            {
                "afpInstanceId": afpInstanceId,
                "reportId": tblReportId,
                "fileObjectName": fileObjectName,
                "fileData": executeResult,
                "assessmentFlowInstanceId": reportResult['content']['flowInstanceId']
            }
        ], },

        'history_data': {'hObjectName': fileObjectName,
                         'pObjectName': reportResult['content']['fileName']['objPath'],
                         "reportId": tblReportId,
                         "reportName": fileName,
                         'afpInstanceId': afpInstanceId,
                         'assessmentFlowInstanceId': assessmentFlowInstanceId,
                         'reportResultId': reportResultId,
                         'fieldsPrivilege': content[0]['fieldsPrivilege'],
                         "fileData": executeResult,
                         'templateObjectName': reportDetail['content']['fileName'], }
    }
    # 更新id
    huixin_app.police_report_result(id=id)

    return data


def audit_out_prison_recidivism_table(audit_level='一般', user_type=HUIXIN_USER.prison_police,
                                      huixin_app: HuiXin = HuiXin):
    audit_data = huixin_app.police_audit_data(user_type=user_type)
    criminal_info = huixin_app.criminal_information['baseinfo']
    fileName = f"history/{audit_data['reportResult']['afpInstanceId']}/@再犯罪评估【报告】@{int(time.time() * 1000)}.docx"

    # 获取当前用户角色
    current_role = huixin_app.current_user.value
    # 通过映射关系直接获取审核字段并添加审核信息
    if current_role not in audit_user:
        huixin_app.current_process_information['audit_user'][current_role] = {
            "auditor": current_role,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    file_data = {
        "id": criminal_info['id'],
        "xq": criminal_info['xq'],
        "yx": criminal_info['yx'],
        "sex": criminal_info['sex'],
        "name": criminal_info['name'],
        "wushe": criminal_info['$WuShe'],
        "dqxqzr": criminal_info.get('DQXQZR', "2030-01-10 00:00:00"),
        "dqxxqr": criminal_info.get('DQXQQR', "2001-01-10 00:00:00"),
        "nation": "汉族",
        "period": "出监",
        "crimelg": "否",
        "__extend": {
            "easyFlow": "否"
        },
        "birthday": criminal_info.get('birthday', "1990-01-10 00:00:00"),
        "zfzlevel": "较高",
        "__DateNow": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "education": "本科及以上未毕业",
        "crime_name": "贩卖毒品",
        "enter_data": "2011-11-10 00:00:00",
        "isVeryHigh": True,
        "recordInfo": [],
        "up_explain": "曾吸毒，成瘾性大，可能因复吸再次实施犯罪行为;预谋性攻击强，增加再犯风险;有犯罪经历，增加再犯风险;月均电话消费低于狱内大部分，与外部社会联系较少，社会支持较差;自尊程度较低，个体可能因为无法正确对待他人的评价而影响行为，情绪等，甚至出现攻击性行为，增加再犯风险;以上5个因素为该罪犯再犯罪风险的重要因素，使该罪犯的再犯罪风险增加。",
        "penaldetail": '',
        "preson_area": "一监区",
        "__PrisonName": "德阳监狱",
        "down_explain": "与同事关系好，人际关系处理融洽，具有良好的社交能力，降低再犯风险;有技能证书，谋生能力较强，应对生活压力方面，抗风险能力强，降低再犯罪风险;以上2个因素为该罪犯再犯罪风险的重要因素，使该罪犯的再犯罪风险降低。",
        "isCustomFlow": True,
        "isSimpleFlow": False,
        "marriage_now": "已婚",
        "native_place": "贵州省盘州市",
        "reviewresults": '',
        "family_address": "贵州省盘州市马场乡业嘎村一组",
        "isExecOutPrison": False,
        "review_zfzlevel": [
            audit_level
        ],
        "simple_zfzlevel": "scriptError:SimpleInfoQuery[0].zfz_result",
        "recordInfolength": 0,
        "crime_record_count": "无",
        "recrimeConclusionQuery": "建议从家庭支持系统方面加强教育和关注，加强法律知识教育，提高职业技能培训，加强社区帮教，提高遵纪守法意识。",
        "reason": '',
        "measure": '',
        "policeopinion": "自动化-民警-审核",
        "prisonopinion": "自动化-领导-审核",
        "assessmentcentreopinion": "自动化-评估中心-审核",
        "__auditInfo": huixin_app.current_process_information['audit_user']
    }
    data = {
        'id': huixin_app.current_process_information['reportResult']['audit_id'],
        'audit_data': {
            "reportFileData": [{
                "afpInstanceId": audit_data['reportResult']['afpInstanceId'],
                "assessmentFlowInstanceId": audit_data['reportResult']['flowInstanceId'],
                "reportId": audit_data['reportResult']['tblReportId'],
                "fileData": file_data,
                "fileObjectName": fileName,
            }]
        },
        'history_data': {
            "hObjectNameList": [{
                "afpInstanceId": audit_data['reportResult']['afpInstanceId'],
                "assessmentFlowInstanceId": audit_data['reportResult']['flowInstanceId'],
                "reportId": audit_data['reportResult']['tblReportId'],
                "templateObjectName": "template/bEWFd4hRu.docx",
                "hObjectName": fileName,
                "pObjectName": audit_data['reportResult']['fileName']['objPath'],
                "reportResultId": audit_data['reportResult']['id'],
                "reportName": "再犯罪评估【报告】",
                "fileData": file_data,
                "fieldsPrivilege": [
                    {
                        "item": "name",
                        "privilege": "VIEW"
                    },
                    {
                        "item": "id",
                        "privilege": "VIEW"
                    },
                    {
                        "item": "preson_area",
                        "privilege": "VIEW"
                    },
                    {
                        "item": "zfzlevel",
                        "privilege": "VIEW"
                    },
                    {
                        "item": "simple_zfzlevel",
                        "privilege": "HIDDEN"
                    },
                    {
                        "item": "review_zfzlevel",
                        "privilege": "EDIT"
                    },
                    {
                        "item": "reason",
                        "privilege": "HIDDEN"
                    },
                    {
                        "item": "measure",
                        "privilege": "HIDDEN"
                    },
                    {
                        "item": "policeopinion",
                        "privilege": "EDIT"
                    },
                    {
                        "item": "prisonopinion",
                        "privilege": "HIDDEN"
                    },
                    {
                        "item": "assessmentcentreopinion",
                        "privilege": "HIDDEN"
                    }
                ]}],
            "stepName": huixin_app.current_user.value}
    }

    return data
