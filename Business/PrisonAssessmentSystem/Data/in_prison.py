import time
from datetime import datetime

from Business.PrisonAssessmentSystem.API import HuiXin
from Business.PrisonAssessmentSystem.Data import ProcessNode
from Business.PrisonAssessmentSystem.Service.HuiXinService import HuiXinService


class In_DataFactory:
    """数据工厂类：统一管理所有测试数据的生成逻辑"""

    def __init__(self, huiXinService: HuiXinService):
        self.huixin_server = huiXinService
        self.audit_user = {}

    # ------------------------------
    # 犯罪情况数据生成
    # ------------------------------
    @staticmethod
    def create_criminal_fzqk_data(huixin_app: HuiXin):
        """生成【犯罪情况】数据"""

        def data_generator():
            try:
                time.sleep(2)  # 模拟接口延迟
                # 获取流程信息和罪犯基本信息
                process_info = huixin_app.police_get_current_process_information(
                    processNode=ProcessNode.犯罪情况
                )
                criminal_info = huixin_app.criminal_information['baseinfo']

                # 组装数据（保持原格式不变）
                return {
                    "data": {
                        "crimeNameField": criminal_info['name'],
                        "pusherField": process_info['data']['pusherField'],
                        "crimeIdField": [criminal_info['id']],
                        "instanceField": process_info['data']['instanceField'],
                        "criminalIdentityField": "user",
                        'crime_situation': {
                            "name": criminal_info['name'],
                            "crime_num": criminal_info['id'],
                            "crime_name": criminal_info['crime_name'],
                            "zx__type": "有期徒刑",
                            "ypxqr": criminal_info['DQXQQR'],
                            "ypxzr": criminal_info['DQXQZR'],
                            "fzxt": "犯罪既遂",
                            "xaflb": "一般刑事犯",
                            "ywqk": "无",
                            "record_info": {},
                            "sddj": ["否"],
                            "ssdj": ["无"],
                            "sjzz": ["否"],
                            "rztd": "承认犯罪事实，有较强的赎罪感",
                            "bdzzql": "无",
                            "mscc": "无",
                            "mspc": "无",
                            "fjqk": "无",
                            "lcza": ["否"],
                            "sfczgf": "否",
                            "ybhrgx": ["亲属"],
                            "jwbs_gsjd": "不详",
                            "jwbs_ssldnlcdjd": "无"
                        }
                    },
                    "formId": process_info['formId'],
                    "updateTime": ''
                }
            except Exception as e:
                huixin_app.logger.error(f"生成【犯罪情况】数据失败: {str(e)}")
                raise AssertionError(f"【犯罪情况】数据生成失败: {str(e)}")

        return data_generator

    # ------------------------------
    # 身心健康表数据生成
    # ------------------------------

    def create_in_prison_body_heart_health_data(self, processNode: ProcessNode):
        """生成【身心健康表】数据"""

        def data_generator():
            try:
                # 获取流程信息和罪犯基本信息
                self.huixin_server.logger.debug("===== 开始执行 data_generator 生成数据 =====")
                process_info = self.huixin_server.current_process_information['currentNode']

                criminal_info = self.huixin_server.criminal_information['baseinfo']

                # 组装数据
                # 获取流程信息和罪犯基本信息
                data = {
                    "data": {
                        "crimeNameField": criminal_info['name'],
                        "pusherField": process_info['afpTaskDetail']['data']['pusherField'],
                        "packageInstanceId": process_info['afpTaskDetail']['data']['packageInstanceId'],
                        "crimeIdField": [criminal_info['id']],
                        "instanceField": process_info['afpTaskDetail']['data']['instanceField'],
                        "crimeid": criminal_info['id'],
                        "crimename": criminal_info['name'],
                        "personarea": criminal_info['preson_area'],
                        "fieldbundr24qme": "血常规",
                        "wbc": 1,
                        "lymph": 2,
                        "gran": 3,
                        "rbc": 4,
                        "hgb": 5,
                        "plt": 6,
                        "xcg_report_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "fieldun8m2d1o8h": "肝功",
                        "alt": 7,
                        "ast": 8,
                        "ast_alt_ratio": 9,
                        "tp": 10,
                        "alb": 11,
                        "glo": 12,
                        "gg_report_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "criminalIdentityField": "user"
                    },
                    "formId": process_info['afpTaskDetail']['formId'],
                    "updateTime": ""
                }
                self.huixin_server.logger.debug("===== 开始执行 data_generator 生成数据成功  =====")
                self.huixin_server.logger.debug(f"<UNK>: {str(data)}")
                return data
            except Exception as e:
                self.huixin_server.logger.error(f"生成【身心健康表】数据失败: {str(e)}")
                raise f"【身心健康表】数据生成失败: {str(e)}"

        return data_generator

    # ------------------------------
    # 体检表数据生成
    # ------------------------------
    def create_in_prison_medical_form_data(self, processNode: ProcessNode):
        """生成【体检表】数据"""

        def data_generator():
            try:
                time.sleep(2)  # 模拟接口延迟
                # 获取流程信息和罪犯基本信息
                self.huixin_server.logger.debug("===== 体检数据表生成 =====")
                process_info = self.huixin_server.current_process_information['currentNode']

                criminal_info = self.huixin_server.criminal_information['baseinfo']

                # 组装数据
                return {
                    "data": {
                        "crimeNameField": criminal_info['name'],
                        "pusherField": process_info['afpTaskDetail']['data']['pusherField'],
                        "crimeIdField": [criminal_info['id']],
                        "instanceField": process_info['afpTaskDetail']['data']['instanceField'],
                        "fieldovigp4aztf": "基本信息",
                        "base_info": {
                            "name": criminal_info['name'],
                            "crime_num": criminal_info['id'],
                            "sex": criminal_info['sex'],
                            "national": criminal_info.get('nation', '汉族'),
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
                        "ybzt_xx": ["A"],
                        "ybzt_tw": 37,
                        "ybzt_xy": [{"shousuoya": 40, "shuzhangya": 300}],
                        "field3ac8v8j3mx": "内科",
                        "nk_xz": [{"nk_xzxl": 100, "nk_xzxlbq": ["齐"], "nk_xzzy": ["无"]}],
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
                        "wgk_lyslz": ["1.0"],
                        "wgk_lysly": ["1.0"],
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
                    "formId": process_info['afpTaskDetail']['formId'],
                    "updateTime": ""
                }
            except Exception as e:
                self.huixin_server.logger.error(f"生成【体检表】数据失败: {str(e)}")
                raise f"【体检表】数据生成失败: {str(e)}"

        return data_generator

    # ------------------------------
    # 【罪犯填写】改造难易-入监问卷数据
    # ------------------------------
    def create_in_prison_transformation_difficultly(self):
        """生成【改造难易-入监问卷】数据"""

        def data_generator():
            try:
                # 获取流程信息
                id, task_info = self.huixin_server.criminal_pre_sheet_submit_info('改造难易-入监问卷')
                # 组装数据
                return {
                    'afpTaskId': id,
                    "data": {
                        "crimePusherField": task_info['data']['crimePusherField'],
                        "crimeNameField": task_info['data']['crimeNameField'],
                        "packageInstanceId": task_info['data']['packageInstanceId'],
                        "crimeIdField": task_info['data']['crimeIdField'],
                        "instanceField": task_info['data']['instanceField'],
                        "fieldn1yvmzzs3f": "<p><span class=\"ql-size-large\">您好！为有利于您更好地改造，我们希望了解您的个人特点及成长经历，请按照您的实际情况认真在答题卷上做出真实可信的回答，全部回答后点击提交。如果您在填写过程中遇到困难，请向民警寻求帮助。</span></p>",
                        "crimeid": task_info['data']['crimeIdField'][0],
                        "crimename": task_info['data']['crimeNameField'],
                        "presonarea": self.huixin_server.criminal_information['baseinfo']['preson_area'],
                        "an13": 49,
                        "an15": "4",
                        "an16": "1",
                        "an31": "0",
                        "an310": "0",
                        "an312": "1",
                        "an314": "1",
                        "an323": "1",
                        "an35": "0",
                        "an38": "1",
                        "an510": "1",
                        "an72": "4",
                        "an75": "2",
                        "an77": "4",
                        "an813f": "2",
                        "an817f": "2",
                        "an818am": "2",
                        "an81af": "2",
                        "an822m": "2",
                        "an85m": "2",
                        "an85oeoeae1m": "2",
                        "an85of": "2",
                        "an86aeaa1m": "2",
                        "an86m": "2",
                        "an87aaaeaa1m": "2",
                        "an911": "2",
                        "an912": "2",
                        "an917": "2",
                        "an922": "2",
                        "an927": "2",
                        "an933": "2",
                        "an94": "2",
                        "an99": "1",
                        "bn513": "2",
                        "bn514": "2",
                        "bn519": "2",
                        "bn57": "2",
                        "field2mqvbnynwo": 54,
                        "criminalIdentityField": "criminal",
                        "pusherField": ["admin"]
                    },
                    "formId": task_info['formId'],
                    "updateTime": ""
                }
            except Exception as e:
                self.huixin_server.logger.error(f"生成【改造难易-入监问卷】数据失败: {str(e)}")
                raise AssertionError(f"【改造难易-入监问卷】数据生成失败: {str(e)}")

        return data_generator

    # ------------------------------
    # 【罪犯填写】罪犯基本信息采集表数据
    # ------------------------------
    def create_inmate_criminal_base_info_table(self):
        """生成【罪犯基本信息采集表】数据"""

        def data_generator():
            try:
                # 获取流程信息
                # 获取流程信息
                id, task_info = self.huixin_server.criminal_pre_sheet_submit_info('罪犯基本信息采集表')
                criminal_info = self.huixin_server.criminal_information['baseinfo']
                data = {
                    'afpTaskId': id,
                    "data": {
                        "crimePusherField": task_info['data']['crimePusherField'],
                        "crimeNameField": task_info['data']['crimeNameField'],
                        "packageInstanceId": task_info['data']['packageInstanceId'],
                        "crimeIdField": task_info['data']['crimeIdField'],
                        "instanceField": task_info['data']['instanceField'],
                        "fielddhv3tsip9": "基本信息",
                        "base_info": {
                            "name": criminal_info['name'],
                            "idcard": criminal_info.get('id_num', ''),
                            "crime_num": criminal_info['id'],
                            "sex": criminal_info['sex'],
                            'height': 175,
                            "birth_date": criminal_info['birthday'],
                            'birth_place': {
                                "region": [
                                    {
                                        "code": "110000",
                                        "name": "北京市"
                                    },
                                    {
                                        "code": "110100",
                                        "name": "市辖区"
                                    },
                                    {
                                        "code": "110101",
                                        "name": "东城区"
                                    }
                                ],
                                "detail": "测试"
                            },
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
                            "fk_qt": "无异常",
                            "nationality": "中国",
                            "weight": 120,
                            "shoe_size": 40,
                            "politics_status": "群众",
                            "police_history": "否",
                            "soldiers_history": "否",
                            "zjxy": "无",
                            'hk_type': '非农业',
                            'national': criminal_info.get('nation', '汉族'),
                        },

                        "fieldxpey3ecs4": "学校教育",
                        "whcd": "本科及以上未毕业",
                        "bljl": ["无"],
                        "lajl": "无",
                        "ssgx": "好",
                        "txgx": "好",
                        "zxjl": "否",
                        "fieldchs6efdfa": "工作就业",
                        "bqzy": "阿萨德",
                        "gzmyd": "满意",
                        "pjgzsc": "8-12小时",
                        "tsgx": "好",
                        "glzzjl": "无",
                        "aqgqpx": "否",
                        "ldjn": "无",
                        "zgzs": "有",
                        "zs_name": ["法律职业资格"],
                        "bqsrly": ["家庭支助", "朋友支助"],
                        "bqjjzk": "好",
                        "fieldcvvsiuosto": "爱好特长",
                        "sfyxqah": "无",
                        "jyjn": ["无"],
                        "fieldtspoqjjwgx": "家庭情况",
                        "fieldcs6tvfpzfw": "（一）本人成长的家庭 ",
                        "jtgc": ["完整家庭（父母均在）"],
                        "zvgc": "独生子女",
                        "fqwhcd": "不清楚 ",
                        "mqwhcd": "不清楚 ",
                        "jtgjfs": "放任型(缺乏责任感，放任自由)",
                        "yfqgx": "一般",
                        "ymqgx": "一般",
                        "yxmgx": "一般",
                        "field45nma4j5m8": "一般",
                        "fieldonnt8x3jnh": "一般",
                        "fqzy": "机关、党群、企事业单位负责人",
                        "mqzy": "机关、党群、企事业单位负责人",
                        "jtjjqk": "一般",
                        "cyfzjl": "无",
                        "ysjtjzd": "城市",
                        "fmgx": "一般",
                        "fieldgnfglolys": "（二）本人组建的家庭",
                        "hyzk": "已婚",
                        "yhqk": "无前面三种情况",
                        "pogz": "有固定工作（工作一年以上）",
                        "dsgqmyd": "较满意",
                        "bhhyzk": "无",
                        "znqk": "有子女",
                        "znxq": ["有成年子女"],
                        "cnznqk": [{"cnzn_sex": "女", "cnzn_num": 3}],
                        "rjysr": "4500~7500",
                        "my_zngx": "一般",
                        "my_pogx": "一般",
                        "mxzf": "有",
                        "yzfqk": "自建房",
                        "jtjzd": "乡镇",
                        "jjjf": ["债务(我欠别人钱)", "债权(别人欠我钱)"],
                        "jjjf_money1": 3000,
                        "jjjf_money2": 1221212,
                        "fieldex80rkwfq": "（三）三代以内直系家族情况 ",
                        "zxqsls": ["无"],
                        "fieldtr9pkbzqf": "身心健康状况",
                        "health": "差",
                        "jbqk": ["1212"],
                        "disability": "有残疾，但不影响生活自理",
                        "bqxlqk": "好",
                        "dxjtcy": ["子女"],
                        "dxsj": ["子女教育", "家人生活困难", "子女没人照顾", "老人没人照顾"],
                        "zss": "否",
                        "fieldqqb6qomfq": "幼年经历 （14岁前）",
                        "fieldi3ltfxnrf": "（一）父母离婚事件",
                        "fmlhsj": "否",
                        "field1xk3iww8j": "（二）留守经历",
                        "lsjl": "否",
                        "fieldljojpffio": "（三）老人扶养",
                        "lrfy": "否",
                        "fieldaetzoqqmdx": "（四）本人幼年被侵害经历",
                        "ynqhjl": ["无"],
                        "fieldlrzy4qnwo": "行为习惯",
                        "fielda4o3giw0z0": "（一）吸毒",
                        "xdfd": "是",
                        "xd_age": "18岁以上",
                        "dp_type": ["冰毒"],
                        "xd_num": "多次",
                        "xd_time": "不到1年",
                        "qzjd": "否",
                        "zyjdjl": "无",
                        "field2dnfcqz8s": "（二）饮酒",
                        "yjqk": "否",
                        "fieldw1yzeho7v": "（三）赌博",
                        "dbqk": ["因赌博欠下债务导致生活受影响", "因赌博引发家庭矛盾"],
                        "fieldona3dl8ppx": "（四）上网",
                        "swqk": "否",
                        "fieldjlofi7nyf": "捕前交友",
                        "ypygx": "一般",
                        "hyqk": ["无上述情况"],
                        "fieldyh40ogz68": "普通话使用能力",
                        "tpth": "完全能听懂",
                        "spth": "有时说着有困难",
                        "jlnl": "较强",
                        "fieldl9x0rcvkm": "外语能力",
                        "foreign_languages": "否",
                        "fieldssd5dizhye": "是",
                        "fieldftgxdheoo": "体表痕迹",
                        "tbhj": ["有纹身", "有疤痕"],
                        "wsbw": ["前胸"],
                        "bhqk": ["其他外伤导致的疤痕"],
                        "bhbw": ["前胸"],
                        "fieldurnzngfyf": "行政拘留",
                        "xzjl": "无",
                        "fieldc6zqvbpn0d": "自述",
                        "yxry": ["无"],
                        "yzwbj": "我比周围人强一点",
                        "fz_resion": ["家庭的原因"],
                        "gzxx": "很有信心",
                        "fieldffgjyzc9e": "是否有以下经历并且该经历持续带来情绪困扰 （可多选）",
                        "cxkrjl": ["其他"],
                        "fieldr8we1sv5l6": 2559
                    },
                    "formId": task_info['formId'],
                    "updateTime": ""
                }
                # 组装数据
                return data
            except Exception as e:
                self.huixin_server.logger.error(f"生成【罪犯基本信息采集表】数据失败: {str(e)}")
                raise AssertionError(f"【罪犯基本信息采集表】数据生成失败: {str(e)}")

        return data_generator

    # ------------------------------
    # 【罪犯填写】罪犯行为测试表数据
    # ------------------------------
    def create_inmate_behaviour_assessment_form(self):
        """生成【罪犯行为测试表】数据"""

        def data_generator():
            try:
                # 获取流程信息
                # 获取流程信息
                id, task_info = self.huixin_server.criminal_pre_sheet_submit_info('罪犯行为测试表')
                criminal_info = self.huixin_server.criminal_information['baseinfo']
                # 组装数据
                return {
                    'afpTaskId': id,
                    "data": {
                        "crimePusherField": task_info['data']['crimePusherField'],
                        "crimeNameField": task_info['data']['crimeNameField'],
                        "packageInstanceId": task_info['data']['packageInstanceId'],
                        "crimeIdField": task_info['data']['crimeIdField'],
                        "instanceField": task_info['data']['instanceField'],
                        "fieldn1yvmzzs3f": "<p><span class=\"ql-size-large\">您好！为有利于您更好地改造，我们希望了解您的个人特点及成长经历，请按照您的实际情况认真在答题卷上做出真实可信的回答，全部回答后点击提交。如果您在填写过程中遇到困难，请向民警寻求帮助。</span></p>",
                        "crimeid": task_info['data']['crimeIdField'][0],
                        "crimename": task_info['data']['crimeNameField'],
                        "presonarea": criminal_info['preson_area'],
                        "field36muk5m98q": "<p class=\"ql-align-center\"><span class=\"ql-size-huge\">回答完毕！</span></p>",
                        "fieldsozoo88qui": "<p class=\"ql-align-center\"><span class=\"ql-size-large\">第四题</span></p><p class=\"ql-align-center\"><span class=\"ql-size-huge\">4，0，8，1</span></p><p class=\"ql-align-center\"><span class=\"ql-size-large\">（倒计时结束后，如果没有跳转，请点击“下一步”按钮继续答题）</span></p>",
                        "field7fn2rpoppa": "<p class=\"ql-align-center\"><span style=\"color: rgb(230, 0, 0);\" class=\"ql-size-huge\">本组总共四组数字</span></p><p class=\"ql-align-center\"><span class=\"ql-size-huge\">请记住第四组数字</span></p>",
                        "fieldqi5hzquc73": "<p class=\"ql-align-center\"><span class=\"ql-size-large\">第三题</span><span class=\"ql-size-huge\">﻿</span></p><p class=\"ql-align-center\"><span class=\"ql-size-huge\">8，9，0，5，4，3</span></p><p class=\"ql-align-center\"><span class=\"ql-size-large\">（倒计时结束后，如果没有跳转，请点击“下一步”按钮继续答题）</span></p>",
                        "fieldhsjoqia5yl": "<p class=\"ql-align-center\"><span style=\"color: rgb(230, 0, 0);\" class=\"ql-size-huge\">本组总共四组数字</span></p><p class=\"ql-align-center\"><span class=\"ql-size-huge\">请记住第三组数字</span></p><p class=\"ql-align-center\"><br></p>",
                        "fielduw42whb8oz": "<p class=\"ql-align-center\"><span class=\"ql-size-large\">第二题</span></p><p class=\"ql-align-center\"><span class=\"ql-size-huge\">5，4，3，1，2</span></p><p class=\"ql-align-center\"><span class=\"ql-size-large\">（倒计时结束后，如果没有跳转，请点击“下一步”按钮继续答题）</span></p>",
                        "field866i15s7k0": "<p class=\"ql-align-center\"><span style=\"color: rgb(230, 0, 0);\" class=\"ql-size-huge\">本组总共四组数字</span></p><p class=\"ql-align-center\"><span class=\"ql-size-huge\">请记住第二组数字</span></p><p class=\"ql-align-center\"><br></p>",
                        "field7wha3vm964": "<p class=\"ql-align-center\"><span class=\"ql-size-large\">第一题</span></p><p class=\"ql-align-center\"><span class=\"ql-size-huge\">6，5，7，3</span></p><p class=\"ql-align-center\"><span class=\"ql-size-large\">（倒计时结束后，如果没有跳转，请点击“下一步”按钮继续答题）</span></p>",
                        "field3baqp3tcxe": "<p class=\"ql-align-center\"><span class=\"ql-size-huge\" style=\"color: rgb(230, 0, 0);\">本组总共四组数字</span></p><p class=\"ql-align-center\"><span class=\"ql-size-huge\">请记住第一组数字</span></p>",
                        "fieldcpwquwlzp": "<p><span class=\"ql-size-large\">指导语：根据收集的材料和信息进行综合研判和分析后，参照评估标准，对下表的每一个项目，作出客观的评估判断。</span></p>",
                        "field1gd4tbcq4": "辨色能力",
                        "fieldzjqzshtet": "<p><img src=\"/app-factory-web/s3/sobey/b31e6279-a8aa-40ca-b626-563e83df4c56.png\"></p>",
                        "fieldjahdlkoxo": "<p><br></p><p><img src=\"/app-factory-web/s3/sobey/3d459a4d-a5eb-469a-b7c5-6120ac738e6c.png\"></p>",
                        "question311": "牛",
                        "question312": "羊",
                        "field5ll4olgod": "<p><br></p><p><img src=\"/app-factory-web/s3/sobey/a7fdf74f-45bd-431a-9713-0d0b5b5bf451.png\"></p>",
                        "field18qxebywc": "<p><br></p><p><br></p><p><img src=\"/app-factory-web/s3/sobey/63ad5383-c611-472f-90b0-1a0b4b5904e9.png\"></p>",
                        "question313": "26",
                        "question314": "6",
                        "fieldr4bgvi0dy": "<p>1（牛）</p><p>2（羊）</p><p>3（26）</p><p>4（6）</p>",
                        "fieldrp2eeqeha": "<p>1.色觉正常（选对2题以上）</p><p>2.色觉异常（选错2题以上）</p>",
                        "fieldigjiauzzq": "逻辑认知",
                        "fieldvh0um1vus": "1.计算力",
                        "question111": 35,
                        "question112": 300,
                        "question113": 62,
                        "question114": 42,
                        "fieldkd31ap4lsq": "<p>24+9=？（33）</p><p>60×5=？（300）</p><p>105-43=？（62）</p><p>420÷10=？（42）</p>",
                        "fielda3hhes3jf": "<p>计算力：</p><p>1.较差（答对≤1个题） </p><p>2.一般（答对2-3题）</p><p>3.较好（全对）</p>",
                        "fieldxyrsbbwhnq": "2.理解能力",
                        "fields62kzooxw": "<p><span class=\"ql-size-large\">一个商人刚关上店里的灯, 一男子来到店里并索要钱款。店主打开收银机，收银机内的东西被倒了出来而那个男子逃走了。一位警察很快接到报案。</span></p>",
                        "question131": "对",
                        "question132": "对",
                        "question133": "对",
                        "fieldxtzcui4gr": "<p>（1）抢劫者是一男子。（<strong>对</strong>）</p><p>（2）打开收银机的那个男子是店主。（<strong>对</strong>）\n</p><p>（3）故事中提到了收银机，但没有说里面具体有多少钱。（<strong>对</strong>）</p>",
                        "fieldfiz2ugudyq": "<p>理解能力：</p><p>1.较差（答对≤1个题）</p><p>2.一般（答对2题）</p><p>3.较好（全对）</p>",
                        "field5grjrdgcu": "3.逻辑能力",
                        "question141": "女子",
                        "question142": "7",
                        "question143": "大树",
                        "fieldxb4b0m9zh": "<p>（1）男孩对应男子，女孩对应__？<strong>（女子） </strong></p><p>（2）规律题：9 7 8 9 7 8 9 __8；__的数字是__ <strong>（7）</strong> </p><p>（3）选出不同类的一项（<strong>大树</strong>）</p>",
                        "fieldb8cczvvqj": "<p>逻辑能力：</p><p>1.较差（答对≤1个题）</p><p>2.一般（答对2题）</p><p>3.较好（全对）</p>",
                        "fieldsw1gii9nn": "4.记忆力",
                        "question121": 7,
                        "question122": 4,
                        "question123": 5,
                        "question124": 0,
                        "steps3pgnd574rw": 12,
                        "field3i0uoywab": "<p>问题1：65<strong>7</strong>3第三个数是？&nbsp;（7）</p><p>问题2：5<strong>4</strong>312第二个数是？（4）</p><p>问题3：890<strong>5</strong>43第四个数是？（5）</p><p>问题4：4<strong>0</strong>81第二个数是？（0）</p>",
                        "fieldx9on0irwet": "<p>记忆力：</p><p>1.较差（答对≤1个题）</p><p>2.一般（答对2-3题）</p><p>3.较好（全对）</p>",
                        "field38f6fl0usx": "口头表达能力",
                        "biaoda_answer": ["总是能够清楚地表达我想表达的内容"],
                        "fieldef1r0chcyl": 98,
                        "criminalIdentityField": "criminal",
                        "pusherField": ["admin"]
                    },
                    "formId": task_info['formId'],
                    "updateTime": ""
                }
            except Exception as e:
                self.huixin_server.logger.error(f"生成【罪犯行为测试表】数据失败: {str(e)}")
                raise AssertionError(f"【罪犯行为测试表】数据生成失败: {str(e)}")

        return data_generator

    # ------------------------------
    # 身心健康评估表数据生成
    # ------------------------------
    @staticmethod
    def create_inmate_body_heart_healthy_table(huixin_app: HuiXin):
        """生成【身心健康评估表】数据"""

        def data_generator():
            try:
                # 获取流程信息
                process_list = huixin_app.criminal_task_query_v2()['resultList'][0]['taskVOS']
                process_info = next(
                    (p for p in process_list if p['cbStepName'] == '身心健康评估量表'),
                    None
                )
                if not process_info:
                    raise ValueError("未找到【身心健康评估量表】流程信息")

                criminal_process = huixin_app.criminal_sheet_task(process_info['afpTaskId'])
                criminal_information = huixin_app.criminal_information['baseinfo']

                # 组装数据
                return {
                    'id': process_info['afpTaskId'],
                    "data": {
                        "crimePusherField": criminal_process['data']['crimePusherField'],
                        "crimeNameField": criminal_process['data']['crimeNameField'],
                        "packageInstanceId": criminal_process['data']['packageInstanceId'],
                        "crimeIdField": criminal_process['data']['crimeIdField'],
                        "instanceField": criminal_process['data']['instanceField'],
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
                        "crimename": criminal_information['name'],
                        "crimeid": criminal_information['id'],
                        "an13": criminal_information['age'].replace('岁', ''),
                        "presonarea": criminal_information['preson_area'],
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
                        "timu1_13": "0",
                        "timu1_14": "0",
                        "timu1_15": "0",
                        "timu1_16": "0",
                        "timu1_17": "0",
                        "timu1_18": "0",
                        "timu1_19": "1",
                        "timu1_20": "1",
                        "timu1_21": "0",
                        "timu1_22": "0",
                        "timu1_23": "1",
                        "timu1_24": "0",
                        "timu1_25": "0",
                        "timu1_26": "0",
                        "timu1_27": "0",
                        "timu1_28": "0",
                        "timu1_29": "0",
                        "timu1_30": "1",
                        "timu1_31": "0",
                        "timu1_32": "1",
                        "timu1_33": "0",
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
                        "timu1_45": "1",
                        "timu1_46": "0",
                        "timu1_47": "0",
                        "timu1_48": "0",
                        "timu1_49": "0",
                        "timu1_50": "0",
                        "timu1_51": "0",
                        "timu1_52": "0",
                        "timu1_53": "0",
                        "timu1_54": "1",
                        "timu1_55": "0",
                        "timu1_56": "0",
                        "timu1_57_1": "0",
                        "timu1_57_2": "0",
                        "timu1_57_3": "0",
                        "timu1_57_4": "1",
                        "timu1_57_5": "0",
                        "timu1_57_6": "0",
                        "timu1_58_1": "0",
                        "timu1_58_2": "0",
                        "timu1_58_3": "0",
                        "timu1_58_4": "0",
                        "timu1_58_5": "0",
                        "timu1_58_6": "0",
                        "timu1_58_7": "0",
                        "timu1_58_8": "1",
                        "timu1_58_9": "0",
                        "timu1_58_10": "0",
                        "timu1_58_11": "0",
                        "timu1_58_12": "0",
                        "timu1_58_13": "1",
                        "timu1_58_14": "0",
                        "timu1_58_15": "0",
                        "timu2_1": "0",
                        "timu2_2": "1",
                        "timu2_3": "0",
                        "timu2_4": "0",
                        "timu2_5": "1",
                        "timu2_6": "0",
                        "timu2_7": "1",
                        "timu2_8": "0",
                        "timu2_9": "1",
                        "timu2_10": "1",
                        "timu2_11": "0",
                        "timu3_1": "2",
                        "timu3_2": "3",
                        "timu3_3": "2",
                        "timu3_4": "2",
                        "timu3_5": "2",
                        "timu3_6": "3",
                        "timu3_7": "2",
                        "timu3_8": "3",
                        "timu4_1": "2",
                        "timu4_2": "2",
                        "timu4_3": "2",
                        "timu4_4": "2",
                        "timu4_5": "2",
                        "timu5_1": "3",
                        "timu5_2": "2",
                        "timu5_3": "1",
                        "timu5_4": "2",
                        "timu5_5": "2",
                        "timu6_1": "2",
                        "timu6_2": "2",
                        "timu6_3": "3",
                        "timu6_4": "2",
                        "timu6_5": "2",
                        "timu6_6": "2",
                        "timu6_7": "2",
                        "timu6_8": "3",
                        "timu6_9": "2",
                        "timu6_10": "2",
                        "timu6_11": "2",
                        "timu6_12": "3",
                        "timu6_13": "2",
                        "timu6_14": "2",
                        "timu6_15": "2",
                        "timu6_16": "3",
                        "timu6_17": "2",
                        "timu6_18": "2",
                        "timu6_19": "2",
                        "timu6_20": "3",
                        "timu6_21": "2",
                        "timu6_22": "2",
                        "timu6_23": "3",
                        "timu6_24": "2",
                        "timu6_25": "3",
                        "timu6_26": "2",
                        "timu6_27": "2",
                        "timu6_28": "3",
                        "timu6_29": "2",
                        "timu6_30": "3",
                        "timu6_31": "2",
                        "timu6_32": "2",
                        "timu6_33": "2",
                        "timu7_1": "1",
                        "timu7_2": "0",
                        "timu7_3": "0",
                        "timu7_4": "1",
                        "timu7_5": "0",
                        "timu7_6": "0",
                        "timu7_7": "1",
                        "timu7_8": "0",
                        "timu7_9": "0",
                        "timu7_10": "0",
                        "timu7_11": "1",
                        "timu7_12": "0",
                        "timu7_13": "0",
                        "timu7_14": "1",
                        "timu7_15": "0",
                        "timu7_16": "1",
                        "timu7_17": "0",
                        "timu7_18": "0",
                        "timu7_19": "0",
                        "timu7_20": "1",
                        "timu7_21": "0",
                        "timu7_22": "0",
                        "timu7_23": "1",
                        "timu7_24": "0",
                        "timu7_25": "0",
                        "timu7_26": "1",
                        "timu7_27": "0",
                        "timu7_28": "0",
                        "timu7_29": "0",
                        "timu7_30": "0",
                        "timu7_31": "1",
                        "timu7_32": "0",
                        "timu7_33": "0",
                        "timu7_34": "0",
                        "timu7_35": "0",
                        "timu7_36": "1",
                        "timu7_37": "0",
                        "timu7_38": "0",
                        "timu7_39": "1",
                        "timu7_40": "1",
                        "timu8_1": "2",
                        "timu8_2": "3",
                        "timu8_3": "2",
                        "timu8_4": "2",
                        "timu8_5": "3",
                        "timu8_6": "3",
                        "timu8_7": "2",
                        "timu8_8": "2",
                        "timu8_9": "2",
                        "timu8_10": "2",
                        "timu8_11": "3",
                        "timu8_12": "2",
                        "timu8_13": "3",
                        "timu8_14": "2",
                        "timu8_15": "2",
                        "timu8_16": "3",
                        "timu8_17": "2",
                        "timu8_18": "2",
                        "timu8_19": "3",
                        "timu8_20": "2",
                        "timu8_21": "2",
                        "timu9_1": "2",
                        "timu9_2": "3",
                        "timu9_3": "2",
                        "timu10_1": "2",
                        "timu10_2": "2",
                        "timu10_3": "3",
                        "timu10_4": "2",
                        "timu10_5": "2",
                        "timu10_6": "2",
                        "timu10_7": "3",
                        "timu11_1": "2",
                        "timu11_2": "2",
                        "fieldzc478x4lbj": 562,
                        "criminalIdentityField": "criminal",
                        "pusherField": ["admin"]
                    },
                    "formId": criminal_process['formId'],
                    "updateTime": ""
                }
            except Exception as e:
                huixin_app.logger.error(f"生成【身心健康评估表】数据失败: {str(e)}")
                raise AssertionError(f"【身心健康评估表】数据生成失败: {str(e)}")

        return data_generator


# ------------------------------
# 使用示例
# ------------------------------
if __name__ == "__main__":
    # 假设huixin_app已初始化
    pass
