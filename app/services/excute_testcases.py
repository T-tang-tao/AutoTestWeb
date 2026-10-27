import uuid
from copy import deepcopy
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from threading import Lock, RLock, Thread
from typing import Optional, Dict

from TestRunner.core.TestRunner import TestRunner
from app.services.task_report import DEFAULT_TASK_REPORT_DIR, generate_task_report
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


def _to_public_payload(value):
    """Convert runner details into a detached, JSON-safe result snapshot."""
    if isinstance(value, Enum):
        return _to_public_payload(value.value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if callable(value):
        return getattr(value, "__qualname__", getattr(value, "__name__", type(value).__name__))
    if isinstance(value, dict):
        return {str(key): _to_public_payload(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_public_payload(item) for item in value]
    if hasattr(value, "isoformat") and callable(value.isoformat):
        try:
            return value.isoformat()
        except (TypeError, ValueError):
            pass
    return str(value)


def _failure_summary(final_status: TaskStatus, runner: TestRunner, details: Dict) -> Optional[str]:
    """Return a concise task-level error summary while preserving detailed case results."""
    if final_status == TaskStatus.COMPLETED:
        return None

    runner_error = getattr(runner, "test_set_error", None)
    if runner_error:
        return str(runner_error)

    if final_status == TaskStatus.FAILED:
        case_stats = details.get("progress", {}).get("case_stats", {})
        failed = int(case_stats.get("failed", 0) or 0)
        errors = int(case_stats.get("error", 0) or 0)
        if failed or errors:
            return f"测试套未通过：失败用例 {failed} 个，异常用例 {errors} 个"
        return "测试套执行未通过"

    return "测试任务执行异常"


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
        self.config_payload = {}
        self.result_details = {}
        self.report_path = None
        self.report_error = None

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
        """Attach the TestRunner while it is executing and snapshot its public config."""
        with self._lock:
            self.runner = runner
            self.config_payload = {
                "TestBed": deepcopy(self.config.get("TestBed")),
                "TestSet": deepcopy(self.config.get("TestSet")),
            }

    def capture_runner_result(self, runner: TestRunner) -> Dict:
        """Persist a detached result snapshot before releasing the runner reference."""
        try:
            details = _to_public_payload(runner.get_test_instances_details())
            if not isinstance(details, dict):
                details = {}
        except Exception:
            logger.exception("读取任务结果失败: %s", self.task_id)
            details = {}

        try:
            progress = round(float(runner._calculate_progress()), 2)
        except (AttributeError, TypeError, ValueError):
            progress = self.progress

        with self._lock:
            self.result_details = details
            self.progress = progress
        return details

    def release_runner(self, runner: Optional[TestRunner] = None) -> None:
        """Release the live runner after result details have been saved."""
        with self._lock:
            if runner is None or self.runner is runner:
                self.runner = None

    def set_report_path(self, report_path) -> None:
        """Publish the successfully generated report path."""
        with self._lock:
            self.report_path = Path(report_path)
            self.report_error = None

    def set_report_error(self, message: str) -> None:
        """Record report-generation failure separately from the task result."""
        with self._lock:
            self.report_error = str(message)

    def get_report_path(self):
        """Return the internal report path without exposing it in public payloads."""
        with self._lock:
            return self.report_path

    def delete_report(self) -> None:
        """Delete a cached report when the corresponding task expires."""
        with self._lock:
            report_path = self.report_path
            self.report_path = None

        if report_path is not None:
            try:
                Path(report_path).unlink(missing_ok=True)
            except OSError:
                logger.exception("清理过期任务报告失败: %s", self.task_id)

    @property
    def duration(self) -> float:
        """Elapsed wall time in seconds, live while running and fixed after finish."""
        with self._lock:
            if self.start_time is None:
                return 0.0
            end = self.end_time or datetime.now()
            return round(max(0.0, (end - self.start_time).total_seconds()), 3)

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
        """Return consistent task metadata and JSON-safe results for every lifecycle state."""
        with self._lock:
            runner = self.runner
            task_status = self._status.value
            error = self.error
            start_time = self.start_time
            end_time = self.end_time
            created_at = self.created_at
            result_details = deepcopy(self.result_details)
            config_payload = deepcopy(self.config_payload)
            report_path = self.report_path
            report_error = self.report_error
            progress = self.progress

        if runner is not None:
            try:
                test_instances = _to_public_payload(runner.get_test_instances_details())
            except Exception:
                logger.exception("读取运行中任务结果失败: %s", self.task_id)
                test_instances = result_details
            try:
                progress = round(float(runner._calculate_progress()), 2)
            except (AttributeError, TypeError, ValueError):
                pass
        else:
            test_instances = result_details

        duration = 0.0
        if start_time is not None:
            duration_end = end_time or datetime.now()
            duration = round(max(0.0, (duration_end - start_time).total_seconds()), 3)
        terminal_status = task_status in {status.value for status in TERMINAL_TASK_STATUSES}
        if terminal_status:
            progress = 100.0

        report_available = (
            terminal_status
            and report_path is not None
            and Path(report_path).is_file()
        )

        return {
            "task_id": self.task_id,
            "status": task_status,
            "progress": progress,
            "created_at": created_at.isoformat(timespec="seconds"),
            "start_time": start_time.isoformat(timespec="seconds") if start_time else None,
            "end_time": end_time.isoformat(timespec="seconds") if end_time else None,
            "duration": duration,
            "error": error,
            "config": config_payload,
            "test_instances": test_instances,
            "report_available": report_available,
            "report_url": f"/huixin/getTaskReport/{self.task_id}" if report_available else None,
            "report_error": report_error,
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
            expired_tasks = [
                (task_id, task)
                for task_id, task in self._tasks.items()
                if task.is_expired(cutoff)
            ]
            for task_id, _task in expired_tasks:
                del self._tasks[task_id]

        for _task_id, task in expired_tasks:
            task.delete_report()

        if expired_tasks:
            logger.info("清理过期任务(%s个)", len(expired_tasks))


# ------------------------------
# 任务提交与执行
# ------------------------------
def submit_test_task(config: Dict, params=None, report_dir=None) -> str:
    """Create a task and submit it through the single supported thread executor."""
    task_manager = TestTaskManager()
    task_id = task_manager.create_task(config)
    thread = Thread(
        target=run_test_task,
        args=(task_id, params, report_dir),
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


def _generate_report_for_task(task, runner, details, report_dir=None) -> None:
    """Generate a report without allowing report failures to overwrite task status."""
    target_dir = report_dir if report_dir is not None else DEFAULT_TASK_REPORT_DIR
    try:
        report_path = generate_task_report(
            task.task_id,
            details,
            runner_stats=getattr(runner, "stats", None),
            report_dir=target_dir,
        )
        task.set_report_path(report_path)
    except Exception:
        task.set_report_error("HTML 报告生成失败")
        logger.exception("生成任务 HTML 报告失败: %s", task.task_id)


def run_test_task(task_id: str, params=None, report_dir=None) -> None:
    """Execute one task, snapshot its result, and release runner resources."""
    task_manager = TestTaskManager()
    task = task_manager.get_task(task_id)
    if task is None:
        logger.error("任务不存在: %s", task_id)
        return

    runner = None
    try:
        task.transition(TaskStatus.RUNNING)
        runner = TestRunner(config=task.config, params=params)
        task.attach_runner(runner)
        runner.run(async_mode=False)

        final_status = status_from_runner(
            getattr(runner, "test_set_status", None)
        )
        details = task.capture_runner_result(runner)
        _generate_report_for_task(task, runner, details, report_dir)
        task.transition(
            final_status,
            error=_failure_summary(final_status, runner, details),
        )
    except Exception as exc:
        if runner is not None:
            details = task.capture_runner_result(runner)
            _generate_report_for_task(task, runner, details, report_dir)
        try:
            task.transition(TaskStatus.ERROR, error=exc)
        except InvalidTaskTransition:
            logger.exception("任务已进入终态，无法再次更新状态: %s", task_id)
        logger.error("任务执行失败: %s", exc, exc_info=True)
    finally:
        if runner is not None:
            # Publish the cached result before clearing live instances so concurrent
            # status queries never observe an empty result during cleanup.
            task.release_runner(runner)
            cleanup = getattr(runner, "cleanup_resources", None)
            if callable(cleanup):
                try:
                    cleanup()
                except Exception:
                    logger.exception("释放 TestRunner 资源失败: %s", task_id)
