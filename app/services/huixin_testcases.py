"""HuiXin-specific assessment-to-test-case mapping.

This compatibility adapter is kept outside the generic task execution service.
New API clients should submit explicit test case paths to POST /api/v1/tasks.
"""

from utils.LoggerManager import LoggerManager

logger = LoggerManager().get_logger()


def get_huixin_test_cases(assessment_config):

    """
    执行测试任务：根据评估类型返回对应的测试用例列表
    Args:
        assessment_config (dict): 评估配置字典，需包含 'assessment' 键
    Returns:
        list: 测试用例字典列表（每个用例包含 'path' 和 'name'），若不支持则返回空列表
    """
    # 校验输入参数，避免 KeyError
    if not isinstance(assessment_config, dict) or "assessment" not in assessment_config:
        logger.error("无效的评估配置：缺少 'assessment' 字段或配置不是字典")
        return []

    assessment = assessment_config["assessment"]
    # 测试用例映射表：键为评估类型，值为对应的测试用例列表
    test_case_map = {
        'in_all': [
            {
                'path': 'PrisonAssessmentSystem/TestCases/Assessment/InPrison/inmate_assessment_criminal_base_info_01.py',
                'name': 'inmate_assessment_criminal_base_info_01',
            },
            {
                'path': 'PrisonAssessmentSystem/TestCases/Assessment/InPrison/inmate_assessment_body_heart_healthy_01.py',
                'name': 'inmate_assessment_body_heart_healthy_01',
            },
            {
                'path': 'PrisonAssessmentSystem/TestCases/Assessment/InPrison/inmate_assessment_vocational_skills_01.py',
                'name': 'inmate_assessment_vocational_skills_01',
            },
            {
                'path': 'PrisonAssessmentSystem/TestCases/Assessment/InPrison/inmate_assessment_personal_risk_01.py',
                'name': 'inmate_assessment_personal_risk_01',
            },
            {
                'path': 'PrisonAssessmentSystem/TestCases/Assessment/InPrison/inmate_assessment_retrofitting_difficultly_01.py',
                'name': 'inmate_assessment_retrofitting_difficultly_01',
            }
            # 可在此处添加更多属于 'in_base' 的测试用例
        ],
        'in_base': [
            {
                'path': 'PrisonAssessmentSystem/TestCases/Assessment/InPrison/inmate_assessment_criminal_base_info_01.py',
                'name': 'inmate_assessment_criminal_base_info_01',
            }
            # 可在此处添加更多属于 'in_base' 的测试用例
        ],
        'in_risk': [
            {
                'path': 'PrisonAssessmentSystem/TestCases/Assessment/InPrison/inmate_assessment_personal_risk_01.py',
                'name': 'inmate_assessment_personal_risk_01',
            }
            # 可在此处添加更多属于 'in_risk' 的测试用例
        ],
        'in_difficulty': [
            {
                'path': 'PrisonAssessmentSystem/TestCases/Assessment/InPrison/inmate_assessment_retrofitting_difficultly_01.py',
                'name': 'inmate_assessment_retrofitting_difficultly_01',
            }
            # 可在此处添加更多属于 'in_difficulty' 的测试用例
        ],
        'in_skill': [
            {
                'path': 'PrisonAssessmentSystem/TestCases/Assessment/InPrison/inmate_assessment_vocational_skills_01.py',
                'name': 'inmate_assessment_vocational_skills_01',
            }
            # 可在此处添加更多属于 'in_skill' 的测试用例
        ],
        'in_health': [
            {
                'path': 'PrisonAssessmentSystem/TestCases/Assessment/InPrison/inmate_assessment_body_heart_healthy_01.py',
                'name': 'inmate_assessment_body_heart_healthy_01',
            }
            # 可在此处添加更多属于 'in_health' 的测试用例
        ],
        'mid_risk': [
            {
                'path': 'PrisonAssessmentSystem/TestCases/Assessment/MidPrison/mid_assessment_risk_01.py',
                'name': 'mid_assessment_risk_01',
            }
            # 可在此处添加更多属于 'mid_base' 的测试用例
        ],
        'mid_health': [
            {
                'path': 'PrisonAssessmentSystem/TestCases/Assessment/MidPrison/middle_assessment_body_heart_healthy_01.py',
                'name': 'middle_assessment_body_heart_healthy_01',
            }
            # 可在此处添加更多属于 'mid_healthy' 的测试用例
        ],
        'mid_skill': [
            {
                'path': 'PrisonAssessmentSystem/TestCases/Assessment/MidPrison/middle_assessment_body_heart_healthy_01.py',
                'name': 'middle_assessment_body_heart_healthy_01',
            }
            # 可在此处添加更多属于 'mid_skill' 的测试用例
        ],
        'mid_interview': [
            {
                'path': 'PrisonAssessmentSystem/TestCases/Assessment/MidPrison/middle_assessment_interview_01.py',
                'name': 'middle_assessment_interview_01',
            }
            # 可在此处添加更多属于 'mid_skill' 的测试用例
        ],
        'mid_difficulty': [
            {
                'path': 'PrisonAssessmentSystem/TestCases/Assessment/MidPrison/middle_assessment_retrofitting_difficultly_01.py',
                'name': 'middle_assessment_retrofitting_difficultly_01',
            }
            # 可继续添加其他评估类型（如 'in_difficulty'、'mid_risk' 等）
        ],
        'mid_reform': [
            {
                'path': 'PrisonAssessmentSystem/TestCases/Assessment/MidPrison/middle_assessment_confession_reform_01.py',
                'name': 'middle_assessment_confession_reform_01',
            }
        ],
        'out_all': [
            {
                'path': 'PrisonAssessmentSystem/TestCases/Assessment/OutPrison/out_prison_01.py',
                'name': 'out_prison_01',
            }
        ],
    }

    # 查找对应的测试用例，不存在则返回空列表并日志告警
    if assessment in test_case_map:
        return test_case_map[assessment]
    else:
        logger.error(f"不支持的评估类型: {assessment}")
        return []
