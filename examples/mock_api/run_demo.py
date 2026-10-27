"""Run the repository's TestRunner and task service against a local Mock API.

With no --base-url, the demo starts an ephemeral loopback server and shuts it
down after execution. The task runs through the actual process-local background
executor; an HTML report is generated from its cached result snapshot.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from threading import Thread
from typing import Optional

import requests
import yaml
from werkzeug.serving import make_server


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_DIR = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from TestRunner.core.Base import StepStatus, TestStatus  # noqa: E402
from TestRunner.extensions.ReportGenerator import ReportGenerator  # noqa: E402
from app.services.excute_testcases import TestTaskManager, submit_test_task  # noqa: E402
from examples.mock_api.server import create_app  # noqa: E402
from utils.task_state import TERMINAL_TASK_STATUSES  # noqa: E402


CONFIG_PATH = EXAMPLE_DIR / "config.example.yml"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports" / "mock-api-demo-report.html"


def _wait_for_health(base_url: str, attempts: int = 40) -> None:
    """Wait briefly for the local or separately started service to be ready."""
    last_error = None
    for _ in range(attempts):
        try:
            response = requests.get(f"{base_url.rstrip('/')}/health", timeout=0.25)
            if response.status_code == 200 and response.json().get("status") == "ok":
                return
            last_error = RuntimeError(
                f"Mock API 健康检查失败: HTTP {response.status_code}"
            )
        except requests.RequestException as exc:
            last_error = exc
        time.sleep(0.025)
    raise RuntimeError(f"Mock API 未就绪: {last_error}")


def _as_enum(enum_type, value, fallback):
    """Translate public string statuses back to report template enum members."""
    for member in enum_type:
        if member.value == value:
            return member
    return fallback


def _build_report_results(test_cases):
    """Adapt TestRunner's public result shape to ReportGenerator's contract."""
    results = []
    for case in test_cases:
        results.append({
            "name": case.get("test_instance_name") or case.get("test_class_name") or "未命名用例",
            "status": _as_enum(
                TestStatus,
                case.get("test_status"),
                TestStatus.ERROR,
            ),
            "duration": case.get("duration") or 0,
            "steps": [
                {
                    "name": step.get("name") or "未命名步骤",
                    "status": _as_enum(
                        StepStatus,
                        step.get("status"),
                        StepStatus.ERROR,
                    ),
                }
                for step in case.get("steps", [])
            ],
        })
    return results


def run_demo(
    base_url: Optional[str] = None,
    report_path: Optional[str] = None,
) -> dict:
    """Run all sample cases through TestTaskManager and return a JSON summary."""
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    # Resolve case paths against this example folder rather than the caller's CWD.
    config["base_dir"] = str(EXAMPLE_DIR)

    target_report = Path(report_path).expanduser() if report_path else DEFAULT_REPORT_PATH
    if not target_report.is_absolute():
        target_report = Path.cwd() / target_report
    target_report = target_report.resolve()

    mock_server = None
    server_thread = None

    if base_url is None:
        mock_server = make_server(
            "127.0.0.1",
            0,
            create_app(),
            threaded=True,
        )
        base_url = f"http://127.0.0.1:{mock_server.server_port}"
        server_thread = Thread(target=mock_server.serve_forever, daemon=True)
        server_thread.start()

    base_url = base_url.rstrip("/")
    try:
        _wait_for_health(base_url)
        task_id = submit_test_task(config, params={"base_url": base_url})
        manager = TestTaskManager()
        task = manager.get_task(task_id)
        terminal_values = {status.value for status in TERMINAL_TASK_STATUSES}
        deadline = time.monotonic() + 30

        while task is not None and task.status not in terminal_values:
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Mock API 测试任务超时: {task_id}")
            time.sleep(0.01)

        if task is None:
            raise RuntimeError(f"无法查询刚创建的测试任务: {task_id}")

        task_payload = task.to_dict()
        suite_details = task_payload.get("test_instances") or {}
        case_details = suite_details.get("test_cases", [])
        stats = {
            "total": len(case_details),
            "passed": sum(
                case.get("test_status") == TestStatus.PASS.value
                for case in case_details
            ),
            "failed": sum(
                case.get("test_status") == TestStatus.FAIL.value
                for case in case_details
            ),
            "error": sum(
                case.get("test_status") == TestStatus.ERROR.value
                for case in case_details
            ),
            "skipped": sum(
                case.get("test_status") == TestStatus.SKIP.value
                for case in case_details
            ),
        }

        report = ReportGenerator(
            results=_build_report_results(case_details),
            stats=stats,
            report_path=str(target_report),
        )
        report.generate_report()

        cases = []
        for case in case_details:
            cases.append({
                "name": case.get("test_instance_name") or case.get("test_class_name"),
                "status": case.get("test_status"),
                "steps": [
                    {"name": step.get("name"), "status": step.get("status")}
                    for step in case.get("steps", [])
                ],
                "error": case.get("error"),
            })

        return {
            "base_url": base_url,
            "task_id": task_id,
            "task_status": task_payload["status"],
            "status": suite_details.get("status", "错误"),
            "duration": task_payload.get("duration", 0.0),
            "error": task_payload.get("error"),
            "stats": stats,
            "report_path": str(target_report),
            "test_cases": cases,
        }
    finally:
        if mock_server is not None:
            mock_server.shutdown()
            mock_server.server_close()
            if server_thread is not None:
                server_thread.join(timeout=2)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="运行 AutoTestWeb Mock API 示例")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("MOCK_API_BASE_URL"),
        help="连接已启动的 Mock API，例如 http://127.0.0.1:5010；省略则自动启动临时本地服务",
    )
    parser.add_argument(
        "--report-path",
        default=str(DEFAULT_REPORT_PATH),
        help="HTML 报告输出路径（默认 reports/mock-api-demo-report.html）",
    )
    args = parser.parse_args(argv)

    summary = run_demo(args.base_url, args.report_path)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return (
        0
        if summary["task_status"] == "completed" and summary["status"] == TestStatus.PASS.value
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
