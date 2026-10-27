"""Unit tests for task lifecycle and the single background execution entry point.

The service imports the real TestRunner and logger at module import time. Stub
those external collaborators here so tests never read local YAML config or call
the business system.
"""
import importlib.util
import sys
import unittest
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

    def get_test_instances_details(self):
        return {"status": self.test_set_status, "test_cases": []}


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

    def test_lifecycle_records_start_and_end_times(self):
        task_id = self.manager.create_task({})
        task = self.manager.get_task(task_id)

        task.transition(TaskStatus.RUNNING)
        self.assertIsNotNone(task.start_time)
        self.assertIsNone(task.end_time)

        task.transition(TaskStatus.COMPLETED)
        self.assertIsNotNone(task.end_time)
        self.assertEqual(task.to_dict()["progress"], 100.0)

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
        self.assertEqual(task.to_dict()["test_instances"]["status"], "通过")

    def test_execution_maps_runner_failure_to_failed(self):
        task_id = self.manager.create_task({})
        self.service.TestRunner = FailedRunner

        self.service.run_test_task(task_id)

        self.assertEqual(self.manager.get_task(task_id).status, "failed")

    def test_runner_initialization_error_becomes_error_terminal_state(self):
        task_id = self.manager.create_task({})
        self.service.TestRunner = BrokenRunner

        self.service.run_test_task(task_id)

        task = self.manager.get_task(task_id)
        self.assertEqual(task.status, "error")
        self.assertIn("runner initialization failed", task.error)
        self.assertIsNotNone(task.end_time)

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
