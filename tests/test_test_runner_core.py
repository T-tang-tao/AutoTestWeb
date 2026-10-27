"""Core execution tests for the TestRunner, isolated from real services and config."""

import importlib.util
import sys
from datetime import datetime
from enum import Enum
from types import ModuleType
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


class RunnerTestStatus(Enum):
    PASS = "通过"
    FAIL = "失败"
    ERROR = "错误"
    SKIP = "跳过"
    RUNNING = "进行中"
    PENDING = "待执行"


class RunnerStepStatus(Enum):
    PASS = "通过"
    FAIL = "失败"
    ERROR = "错误"
    SKIP = "跳过"
    RUNNING = "进行中"
    PENDING = "待执行"
    AUDIT = "审核中"
    FINISHED = "已完成"


class CaseBase:
    """Small substitute for Base; it preserves the step-plan contract."""

    def __init__(self, **kwargs):
        self.test_status = None
        self.step_plans = []
        self.is_failed = False
        self.execute_start_time = None
        self.execute_end_time = None
        self.duration = 0.0
        self.error = None
        self.case_name = None

    def setUp(self):
        pass

    def defineSteps(self):
        raise NotImplementedError

    def tearDown(self):
        pass

    def def_step(self, step_name, method, args=None, kwargs=None):
        processed_kwargs = {
            key: ({"is_callable": True, "callable": value} if callable(value) else value)
            for key, value in (kwargs or {}).items()
        }
        self.step_plans.append({
            "name": step_name,
            "status": RunnerStepStatus.PENDING.value,
            "method": method,
            "args": args or (),
            "kwargs": processed_kwargs,
        })


class FakeLogger:
    def debug(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


LOGGER = FakeLogger()


def _time_now():
    return datetime.now().strftime("%Y-%m-%d+%H:%M:%S")


def _time_diff(start, end):
    start_dt = datetime.strptime(start, "%Y-%m-%d+%H:%M:%S")
    end_dt = datetime.strptime(end, "%Y-%m-%d+%H:%M:%S")
    return (end_dt - start_dt).total_seconds()


@pytest.fixture
def runner_class(monkeypatch):
    base_module = ModuleType("TestRunner.core.Base")
    base_module.TestStatus = RunnerTestStatus
    base_module.StepStatus = RunnerStepStatus
    base_module.Base = CaseBase

    common_module = ModuleType("utils.Common")
    common_module.time_now = _time_now
    common_module.time_diff = _time_diff
    common_module.HuiXin_login = lambda test_bed: {"mock": "cookie"}

    config_module = ModuleType("utils.ConfigLoader")
    config_module.ConfigLoader = type("ConfigLoader", (), {})

    logger_module = ModuleType("utils.LoggerManager")
    logger_module.LoggerManager = type(
        "LoggerManager",
        (),
        {"get_logger": lambda self: LOGGER},
    )

    for name, module in {
        "TestRunner.core.Base": base_module,
        "utils.Common": common_module,
        "utils.ConfigLoader": config_module,
        "utils.LoggerManager": logger_module,
    }.items():
        monkeypatch.setitem(sys.modules, name, module)

    module_name = "_autotestweb_test_runner_under_test"
    spec = importlib.util.spec_from_file_location(
        module_name, ROOT / "TestRunner" / "core" / "TestRunner.py"
    )
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, module_name, module)
    spec.loader.exec_module(module)
    return module.TestRunner


def _write_case(tmp_path, name, source):
    case_file = tmp_path / f"{name}.py"
    case_file.write_text(source, encoding="utf-8")
    return case_file


def _make_runner(runner_class, tmp_path, *case_files):
    config = {
        "TestBed": {"env": "unit-test"},
        "TestSet": {"test_cases": [{"path": case.name} for case in case_files]},
        "base_dir": str(tmp_path),
    }
    return runner_class(config)


def test_successful_case_runs_lifecycle_and_reports_consistent_stats(
    runner_class, tmp_path
):
    case_file = _write_case(
        tmp_path,
        "passing_case",
        """
from TestRunner.core.Base import Base

class passing_case(Base):
    def setUp(self):
        self.events = ["setUp"]

    def defineSteps(self):
        self.def_step("perform step", self.perform_step)

    def perform_step(self):
        self.events.append("step")

    def tearDown(self):
        self.events.append("tearDown")
""",
    )
    runner = _make_runner(runner_class, tmp_path, case_file)

    runner.run()

    instance = runner.test_instances[0]
    details = runner.get_test_instances_details()
    assert runner.test_set_status == RunnerTestStatus.PASS.value
    assert instance.test_status == TestStatus.PASS.value
    assert instance.events == ["setUp", "step", "tearDown"]
    assert instance.step_plans[0]["status"] == StepStatus.PASS.value
    assert instance.execute_start_time is not None
    assert instance.execute_end_time is not None
    assert runner.stats == {
        "total": 1, "passed": 1, "failed": 0, "error": 0, "skipped": 0
    }
    assert details["progress"]["case_stats"]["passed"] == runner.stats["passed"]
    assert details["progress"]["steps_stats"]["passed_steps"] == 1
    assert runner._calculate_progress() == 100.0


def test_assertion_failure_marks_step_and_skips_remaining_steps(runner_class, tmp_path):
    case_file = _write_case(
        tmp_path,
        "assertion_case",
        """
from TestRunner.core.Base import Base

class assertion_case(Base):
    def defineSteps(self):
        self.after_failure_ran = False
        self.def_step("expected assertion", self.fail)
        self.def_step("must be skipped", self.after_failure)

    def fail(self):
        assert False, "expected failure"

    def after_failure(self):
        self.after_failure_ran = True
""",
    )
    runner = _make_runner(runner_class, tmp_path, case_file)

    runner.run()

    instance = runner.test_instances[0]
    assert runner.test_set_status == TestStatus.FAIL.value
    assert instance.test_status == TestStatus.FAIL.value
    assert [step["status"] for step in instance.step_plans] == [
        StepStatus.FAIL.value, StepStatus.SKIP.value
    ]
    assert instance.step_plans[1]["skip_reason"]
    assert not instance.after_failure_ran
    assert runner.stats["failed"] == 1
    report = runner.get_test_instances_details()
    assert report["progress"]["steps_stats"]["failed_steps"] == 1
    assert report["progress"]["steps_stats"]["skipped_steps"] == 1


def test_runtime_exception_is_distinct_from_assertion_failure(runner_class, tmp_path):
    case_file = _write_case(
        tmp_path,
        "runtime_error_case",
        """
from TestRunner.core.Base import Base

class runtime_error_case(Base):
    def defineSteps(self):
        self.def_step("raises runtime error", self.explode)

    def explode(self):
        raise RuntimeError("dependency unavailable")
""",
    )
    runner = _make_runner(runner_class, tmp_path, case_file)

    runner.run()

    instance = runner.test_instances[0]
    assert runner.test_set_status == TestStatus.FAIL.value
    assert instance.test_status == TestStatus.ERROR.value
    assert instance.step_plans[0]["status"] == StepStatus.ERROR.value
    assert "RuntimeError" in instance.step_plans[0]["error"]
    assert runner.stats["error"] == 1
    assert runner.stats["failed"] == 0


def test_setup_failure_marks_case_error_and_records_end_time(runner_class, tmp_path):
    case_file = _write_case(
        tmp_path,
        "setup_error_case",
        """
from TestRunner.core.Base import Base

class setup_error_case(Base):
    def setUp(self):
        raise RuntimeError("setup failed")

    def defineSteps(self):
        self.def_step("never reached", lambda: None)
""",
    )
    runner = _make_runner(runner_class, tmp_path, case_file)

    runner.run()

    instance = runner.test_instances[0]
    assert instance.test_status == TestStatus.ERROR.value
    assert instance.execute_end_time is not None
    assert "setup failed" in instance.error
    assert runner.stats["error"] == 1
    assert runner.test_set_status == TestStatus.FAIL.value


def test_missing_case_path_is_rejected_during_config_validation(runner_class, tmp_path):
    with pytest.raises(ValueError, match="路径不存在"):
        runner_class({
            "TestBed": {"env": "unit-test"},
            "TestSet": {"test_cases": [{"path": "missing_case.py"}]},
            "base_dir": str(tmp_path),
        })


def test_import_error_prevents_suite_from_being_reported_as_pass(runner_class, tmp_path):
    invalid_file = _write_case(
        tmp_path,
        "invalid_case",
        "this is not valid python syntax !!!\n",
    )
    valid_file = _write_case(
        tmp_path,
        "valid_case",
        """
from TestRunner.core.Base import Base

class valid_case(Base):
    def defineSteps(self):
        self.def_step("pass", self.pass_step)

    def pass_step(self):
        return None
""",
    )
    runner = _make_runner(runner_class, tmp_path, invalid_file, valid_file)

    runner.run()

    assert runner.test_set_status == TestStatus.FAIL.value
    assert runner.load_errors
    assert "SyntaxError" in runner.test_set_error
    assert runner.stats == {
        "total": 2, "passed": 1, "failed": 0, "error": 1, "skipped": 0
    }
    assert runner._calculate_progress() == 100.0


def test_empty_suite_finishes_with_failed_status_and_end_time(runner_class, tmp_path):
    runner = _make_runner(runner_class, tmp_path)

    runner.run()

    assert runner.test_set_status == TestStatus.FAIL.value
    assert runner.test_set_error == "测试套中没有配置用例"
    assert runner.overall_start_time is not None
    assert runner.overall_end_time is not None
    assert not runner.is_running
    assert runner.stats == {
        "total": 0, "passed": 0, "failed": 0, "error": 0, "skipped": 0
    }


def test_runner_instances_keep_results_isolated(runner_class, tmp_path):
    good_file = _write_case(
        tmp_path,
        "isolated_good_case",
        """
from TestRunner.core.Base import Base

class isolated_good_case(Base):
    def defineSteps(self):
        self.def_step("pass", self.pass_step)

    def pass_step(self):
        return None
""",
    )
    bad_file = _write_case(
        tmp_path,
        "isolated_bad_case",
        """
from TestRunner.core.Base import Base

class isolated_bad_case(Base):
    def defineSteps(self):
        self.def_step("fail", self.fail_step)

    def fail_step(self):
        assert False, "only this runner fails"
""",
    )
    good_runner = _make_runner(runner_class, tmp_path, good_file)
    bad_runner = _make_runner(runner_class, tmp_path, bad_file)

    good_runner.run()
    bad_runner.run()

    assert good_runner.test_set_status == TestStatus.PASS.value
    assert bad_runner.test_set_status == TestStatus.FAIL.value
    assert good_runner.test_instances[0].test_status == TestStatus.PASS.value
    assert bad_runner.test_instances[0].test_status == TestStatus.FAIL.value
    assert good_runner.test_instances is not bad_runner.test_instances
