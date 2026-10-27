"""Unit tests for task lifecycle and the single background execution entry point.

The service imports the real TestRunner and logger at module import time. Stub
those external collaborators here so tests never read local YAML config or call
the business system.
"""
import importlib.util
import json
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

from utils.task_state import TaskStatus, InvalidTaskTransition


ROOT = Path(__file__).resolve().parents[1]


class FakeLogger:
    def info(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def exception(self, *args, **kwargs):
        pass


LOGGER = FakeLogger()


class SuccessfulRunner:
    def __init__(self, config, params=None):
        self.config = config
        self.params = params
        self.test_set_status = "通过"
        self.test_set_error = None

    def run(self, async_mode=False):
        self.assert_sync_mode = async_mode is False

    def _calculate_progress(self):
        return 75.0

    def sample_step(self):
        return None

    def get_test_instances_details(self):
        failed = self.test_set_status == "失败"
        return {
            "status": self.test_set_status,
            "progress": {
                "case_stats": {
                    "total_cases": 1,
                    "passed": 0 if failed else 1,
                    "failed": 1 if failed else 0,
                    "error": 0,
                }
            },
            "test_cases": [{
                "test_instance_name": "sample_case",
                "test_status": self.test_set_status,
                "steps": [{
                    "name": "sample step",
                    "status": "通过",
                    "method": self.sample_step,
                    "kwargs": {
                        "deferred": {
                            "is_callable": True,
                            "callable": self.sample_step,
                        }
                    },
                }],
            }],
        }


class FailedRunner(SuccessfulRunner):
    def __init__(self, config, params=None):
        super().__init__(config, params)
        self.test_set_status = "失败"


class BrokenRunner:
    def __init__(self, config, params=None):
        raise RuntimeError("runner initialization failed")


def load_task_service():
    logger_module = ModuleType("utils.LoggerManager")
    logger_module.LoggerManager = type(
        "FakeLoggerManager",
        (),
        {"get_logger": lambda self: LOGGER},
    )

    runner_module = ModuleType("TestRunner.core.TestRunner")
    runner_module.TestRunner = SuccessfulRunner

    stubs = {
        "utils.LoggerManager": logger_module,
        "TestRunner.core.TestRunner": runner_module,
    }
    with patch.dict(sys.modules, stubs):
        module_name = "_autotestweb_task_service_test"
        spec = importlib.util.spec_from_file_location(
            module_name, ROOT / "app" / "services" / "excute_testcases.py"
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    return module


class TaskLifecycleServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = load_task_service()
        self.service.TestTaskManager._instance = None
        self.manager = self.service.TestTaskManager()

    def test_new_task_has_pending_state_and_isolated_config(self):
        config = {"TestSet": {"test_cases": [{"path": "case_a.py"}]}}
        task_id = self.manager.create_task(config)
        task = self.manager.get_task(task_id)

        config["TestSet"]["test_cases"].append({"path": "case_b.py"})
        self.assertEqual(task.status, "pending")
        self.assertEqual(len(task.config["TestSet"]["test_cases"]), 1)
        payload = task.to_dict()
        self.assertEqual(payload["task_id"], task_id)
        self.assertEqual(payload["status"], "pending")
        self.assertIsNone(payload["start_time"])
        self.assertIsNone(payload["end_time"])
        self.assertEqual(payload["duration"], 0.0)
        self.assertEqual(payload["test_instances"], {})
        self.assertEqual(payload["config"], {})

    def test_lifecycle_records_start_and_end_times(self):
        task_id = self.manager.create_task({})
        task = self.manager.get_task(task_id)

        task.transition(TaskStatus.RUNNING)
        self.assertIsNotNone(task.start_time)
        self.assertIsNone(task.end_time)

        running_payload = task.to_dict()
        self.assertGreaterEqual(running_payload["duration"], 0.0)

        task.transition(TaskStatus.COMPLETED)
        self.assertIsNotNone(task.end_time)
        terminal_payload = task.to_dict()
        self.assertEqual(terminal_payload["progress"], 100.0)
        self.assertGreaterEqual(terminal_payload["duration"], 0.0)

    def test_terminal_state_cannot_transition_again(self):
        task_id = self.manager.create_task({})
        task = self.manager.get_task(task_id)
        task.transition(TaskStatus.RUNNING)
        task.transition(TaskStatus.FAILED)

        with self.assertRaises(InvalidTaskTransition):
            task.transition(TaskStatus.RUNNING)

    def test_execution_maps_runner_success_to_completed(self):
        task_id = self.manager.create_task({"TestSet": {"test_cases": []}})
        self.service.TestRunner = SuccessfulRunner

        self.service.run_test_task(task_id, {"sample": True})

        task = self.manager.get_task(task_id)
        self.assertEqual(task.status, "completed")
        self.assertIsNotNone(task.start_time)
        self.assertIsNotNone(task.end_time)
        payload = task.to_dict()
        self.assertEqual(payload["test_instances"]["status"], "通过")
        self.assertEqual(payload["config"]["TestSet"], {"test_cases": []})
        self.assertGreaterEqual(payload["duration"], 0.0)
        self.assertIsNone(task.runner)
        # Bound methods and delayed callables must not keep the runner/case alive.
        self.assertEqual(
            payload["test_instances"]["test_cases"][0]["steps"][0]["method"],
            "SuccessfulRunner.sample_step",
        )
        self.assertEqual(
            payload["test_instances"]["test_cases"][0]["steps"][0]["kwargs"]["deferred"]["callable"],
            "SuccessfulRunner.sample_step",
        )
        json.dumps(payload)

    def test_execution_maps_runner_failure_to_failed(self):
        task_id = self.manager.create_task({})
        self.service.TestRunner = FailedRunner

        self.service.run_test_task(task_id)

        task = self.manager.get_task(task_id)
        self.assertEqual(task.status, "failed")
        self.assertEqual(task.error, "测试套未通过：失败用例 1 个，异常用例 0 个")
        self.assertIsNone(task.runner)
        self.assertEqual(task.to_dict()["test_instances"]["status"], "失败")

    def test_runner_initialization_error_becomes_error_terminal_state(self):
        task_id = self.manager.create_task({})
        self.service.TestRunner = BrokenRunner

        self.service.run_test_task(task_id)

        task = self.manager.get_task(task_id)
        self.assertEqual(task.status, "error")
        self.assertIn("runner initialization failed", task.error)
        self.assertIsNotNone(task.end_time)

    def test_runner_execution_exception_keeps_snapshot_and_releases_runner(self):
        class CrashingRunner(SuccessfulRunner):
            def run(self, async_mode=False):
                raise RuntimeError("execution crashed")

        task_id = self.manager.create_task({"TestSet": {"test_cases": []}})
        self.service.TestRunner = CrashingRunner

        self.service.run_test_task(task_id)

        task = self.manager.get_task(task_id)
        payload = task.to_dict()
        self.assertEqual(task.status, "error")
        self.assertIn("execution crashed", task.error)
        self.assertIsNotNone(task.end_time)
        self.assertIsNone(task.runner)
        self.assertEqual(payload["test_instances"]["status"], "通过")
        json.dumps(payload)

    def test_cleanup_removes_expired_terminal_tasks_but_keeps_running_tasks(self):
        expired_id = self.manager.create_task({})
        running_id = self.manager.create_task({})
        expired = self.manager.get_task(expired_id)
        running = self.manager.get_task(running_id)

        expired.transition(TaskStatus.RUNNING)
        expired.transition(TaskStatus.COMPLETED)
        expired.end_time = datetime.now() - timedelta(hours=2)

        running.transition(TaskStatus.RUNNING)
        running.end_time = datetime.now() - timedelta(hours=2)

        self.manager._cleanup_expired_tasks(max_keep_time=3600)

        self.assertIsNone(self.manager.get_task(expired_id))
        self.assertIs(self.manager.get_task(running_id), running)

    def test_thread_start_failure_marks_task_error_and_records_end_time(self):
        class BrokenThread:
            def __init__(self, target, args, name, daemon):
                self.target = target
                self.args = args

            def start(self):
                raise RuntimeError("thread could not start")

        before = set(self.manager._tasks)
        with patch.object(self.service, "Thread", BrokenThread):
            with self.assertRaisesRegex(RuntimeError, "thread could not start"):
                self.service.submit_test_task({"TestSet": {"test_cases": []}})

        new_ids = set(self.manager._tasks) - before
        self.assertEqual(len(new_ids), 1)
        task = self.manager.get_task(new_ids.pop())
        self.assertEqual(task.status, "error")
        self.assertIn("thread could not start", task.error)
        self.assertIsNotNone(task.end_time)
        self.assertIsNone(task.runner)

    def test_submit_test_task_uses_one_execution_entry_point(self):
        class InlineThread:
            def __init__(self, target, args, name, daemon):
                self.target = target
                self.args = args

            def start(self):
                self.target(*self.args)

        with patch.object(self.service, "Thread", InlineThread):
            task_id = self.service.submit_test_task({"TestSet": {"test_cases": []}})

        self.assertEqual(self.manager.get_task(task_id).status, "completed")


if __name__ == "__main__":
    unittest.main()
