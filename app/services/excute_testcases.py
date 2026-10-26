import uuid
from datetime import datetime
import time
from typing import Optional, Dict

from TestRunner.core.Base import StepStatus
from TestRunner.core.TestRunner import TestRunner
from utils.LoggerManager import LoggerManager
from utils.ConfigLoader import ConfigLoader
from utils.Common import HuiXin_login

# 初始化日志
logger = LoggerManager().get_logger()
ConfigLoader = ConfigLoader()


# ------------------------------
# 任务管理类（TestTask/TestTaskManager）
# ------------------------------
class TestTask:
    """测试任务状态管理（直接关联TestRunner实例）"""

    def __init__(self, task_id: str, config: Dict):
        self.task_id = task_id
        self.config = config
        self.runner = None  # 直接保存TestRunner实例

        self.status = "pending"  # pending/running/completed/failed/cancelled
        self.progress = 0.0
        self.start_time = datetime.now()
        self.end_time = None
        self.error = None

    def attach_runner(self, runner: TestRunner):
        """关联TestRunner实例"""
        self.runner = runner
        self.status = "running"

    @staticmethod
    def calculate_step_pass_percentage(test_instances_details) -> float:
        """
        根据所有步骤的通过情况计算进度百分比
        公式：(通过的步骤数 / 总步骤数) * 100%
        """
        total_steps = 0
        passed_steps = 0

        # 遍历所有测试实例
        for instance in test_instances_details:
            # 遍历当前实例的所有步骤
            for step in instance.get("steps", []):
                total_steps += 1
                # 统计"通过"状态的步骤
                if step.get("status") == "通过":  # 注意：与实际状态值匹配（如"通过"或"PASS"）
                    passed_steps += 1

        # 处理无步骤的特殊情况
        if total_steps == 0:
            return 0.0  # 无步骤时进度为0%（或根据业务需求返回100%）

        # 计算百分比并保留2位小数
        return round((passed_steps / total_steps) * 100, 2)

    def to_dict(self) -> Dict:
        """序列化任务信息（获取最新状态后返回）"""
        config = ConfigLoader.get_config()
        if self.runner:
            test_instances_details = self.runner.get_test_instances_details()
            status = {
                "task_id": self.task_id,
                'config': {
                    'TestBed':config['TestBed'],
                    'TestSet':config['TestSet'],
                },
                "test_instances": test_instances_details  # 获取最新状态
            }
            # logger.info(f'任务状态：{status}')
            return status
        else:
            return {}


class TestTaskManager:
    """全局任务管理器（单例）"""
    _instance = None
    _tasks = {}  # {task_id: TestTask}

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化任务管理器"""
        self.test_instance_lists = []

    def create_task(self, config: Dict) -> str:
        """创建新任务"""
        task_id = str(uuid.uuid4())
        self._tasks[task_id] = TestTask(task_id, config)
        # self._cleanup_expired_tasks()  # 清理过期任务
        return task_id

    def get_task(self, task_id: str) -> Optional[TestTask]:
        """获取任务实例"""
        return self._tasks.get(task_id)

    def _cleanup_expired_tasks(self, max_keep_time: int = 3600):
        """清理1小时前已完成的任务"""
        current_time = time.time()
        expired_ids = []
        for task_id, task in self._tasks.items():
            if task.status in ["completed", "failed", "cancelled"]:
                task_lifetime = current_time - task.start_time.timestamp()
                if task_lifetime > max_keep_time:
                    expired_ids.append(task_id)
        for task_id in expired_ids:
            del self._tasks[task_id]
        if expired_ids:
            LoggerManager().get_logger().info(f"清理过期任务({len(expired_ids)}个)")


# ------------------------------
# 任务执行与回调函数
# ------------------------------
def run_test_task(task_id: str,params):
    """在线程中执行测试任务"""
    task_manager = TestTaskManager()
    task = task_manager.get_task(task_id)
    if not task:
        LoggerManager().get_logger().error(f"任务不存在: {task_id}")
        return

    try:
        # 创建TestRunner并绑定回调
        runner = TestRunner(
            config=task.config,
            params=params,
        )

        # 关联TestRunner实例到任务
        task.attach_runner(runner)
        task_manager.test_instance_lists.append(runner.test_instances)

        # 执行测试（同步模式，由当前线程托管）
        runner.run(async_mode=False)

    except Exception as e:
        task.status = "failed"
        task.error = str(e)
        task.end_time = datetime.now()
        LoggerManager().get_logger().error(f"任务执行失败: {e}", exc_info=True)


def execute_test_task(assessment_config):
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
