import uuid
from copy import deepcopy
from datetime import datetime, timedelta
from threading import Lock, RLock, Thread
from typing import Optional, Dict

from TestRunner.core.TestRunner import TestRunner
from utils.task_state import (
    InvalidTaskTransition,
    TERMINAL_TASK_STATUSES,
    TaskStatus,
    status_from_runner,
    validate_transition,
)
from utils.LoggerManager import LoggerManager

# 初始化日志
logger = LoggerManager().get_logger()


# ------------------------------
# 任务管理类（TestTask/TestTaskManager）
# ------------------------------
class TestTask:
    """维护单个任务的生命周期和执行结果。"""

    def __init__(self, task_id: str, config: Dict):
        self.task_id = task_id
        self.config = deepcopy(config)
        self.runner = None
        self._status = TaskStatus.PENDING
        self._lock = RLock()
        self.progress = 0.0
        self.created_at = datetime.now()
        self.start_time = None
        self.end_time = None
        self.error = None

    @property
    def status(self) -> str:
        return self._status.value

    def transition(self, target: TaskStatus, error=None) -> None:
        """Apply a validated state transition and record lifecycle timestamps."""
        with self._lock:
            next_status = validate_transition(self._status, target)
            now = datetime.now()

            if next_status == TaskStatus.RUNNING and self.start_time is None:
                self.start_time = now
            if next_status in TERMINAL_TASK_STATUSES:
                self.end_time = now
                self.progress = 100.0
            if error is not None:
                self.error = str(error)

            self._status = next_status

    def attach_runner(self, runner: TestRunner) -> None:
        """Attach the TestRunner instance used to execute this task."""
        with self._lock:
            self.runner = runner

    def is_expired(self, cutoff: datetime) -> bool:
        """Check retention under the same lock used for state transitions."""
        with self._lock:
            return (
                self._status in TERMINAL_TASK_STATUSES
                and self.end_time is not None
                and self.end_time < cutoff
            )

    def _current_progress(self) -> float:
        if self.status in {status.value for status in TERMINAL_TASK_STATUSES}:
            return 100.0
        if self.runner is not None:
            try:
                return round(float(self.runner._calculate_progress()), 2)
            except (AttributeError, TypeError, ValueError):
                pass
        return self.progress

    def to_dict(self) -> Dict:
        """Return the same result payload for pending, running and terminal tasks."""
        with self._lock:
            runner = self.runner
            task_status = self.status
            error = self.error
            start_time = self.start_time
            end_time = self.end_time
            created_at = self.created_at
            config = self.config

        test_instances = runner.get_test_instances_details() if runner else {}
        config_payload = {}
        if runner:
            config_payload = {
                "TestBed": config.get("TestBed"),
                "TestSet": config.get("TestSet"),
            }

        return {
            "task_id": self.task_id,
            "status": task_status,
            "progress": self._current_progress(),
            "created_at": created_at.isoformat(timespec="seconds"),
            "start_time": start_time.isoformat(timespec="seconds") if start_time else None,
            "end_time": end_time.isoformat(timespec="seconds") if end_time else None,
            "error": error,
            "config": config_payload,
            "test_instances": test_instances,
        }


class TestTaskManager:
    """Thread-safe process-local registry for submitted test tasks."""

    _instance = None
    _instance_lock = Lock()

    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # __new__ serializes instance creation; guard initialization too because
        # concurrent callers may enter __init__ on the same singleton instance.
        with self._instance_lock:
            if getattr(self, "_initialized", False):
                return
            self._tasks = {}
            self._lock = RLock()
            self._initialized = True

    def create_task(self, config: Dict) -> str:
        """Create an isolated task record and opportunistically expire old tasks."""
        self._cleanup_expired_tasks()
        task_id = str(uuid.uuid4())
        task = TestTask(task_id, config)
        with self._lock:
            self._tasks[task_id] = task
        return task_id

    def get_task(self, task_id: str) -> Optional[TestTask]:
        with self._lock:
            return self._tasks.get(task_id)

    def _cleanup_expired_tasks(self, max_keep_time: int = 3600) -> None:
        """Remove terminal tasks one hour after they finished."""
        cutoff = datetime.now() - timedelta(seconds=max_keep_time)
        with self._lock:
            expired_ids = [
                task_id
                for task_id, task in self._tasks.items()
                if task.is_expired(cutoff)
            ]
            for task_id in expired_ids:
                del self._tasks[task_id]

        if expired_ids:
            logger.info("清理过期任务(%s个)", len(expired_ids))


# ------------------------------
# 任务提交与执行
# ------------------------------
def submit_test_task(config: Dict, params=None) -> str:
    """Create a task and submit it through the single supported thread executor."""
    task_manager = TestTaskManager()
    task_id = task_manager.create_task(config)
    thread = Thread(
        target=run_test_task,
        args=(task_id, params),
        name=f"TestTask-{task_id[:8]}",
        daemon=True,
    )

    try:
        thread.start()
    except Exception as exc:
        task = task_manager.get_task(task_id)
        if task is not None:
            task.transition(TaskStatus.ERROR, error=exc)
        raise

    return task_id


def run_test_task(task_id: str, params=None) -> None:
    """Execute one task and always record a terminal status."""
    task_manager = TestTaskManager()
    task = task_manager.get_task(task_id)
    if task is None:
        logger.error("任务不存在: %s", task_id)
        return

    try:
        task.transition(TaskStatus.RUNNING)
        runner = TestRunner(config=task.config, params=params)
        task.attach_runner(runner)
        runner.run(async_mode=False)

        final_status = status_from_runner(
            getattr(runner, "test_set_status", None)
        )
        runner_error = getattr(runner, "test_set_error", None)
        task.transition(
            final_status,
            error=runner_error if final_status == TaskStatus.ERROR else None,
        )
    except Exception as exc:
        try:
            task.transition(TaskStatus.ERROR, error=exc)
        except InvalidTaskTransition:
            logger.exception("任务已进入终态，无法再次更新状态: %s", task_id)
        logger.error("任务执行失败: %s", exc, exc_info=True)


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
