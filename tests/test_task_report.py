"""Tests for task HTML report conversion, escaping, and download API."""

from pathlib import Path
from uuid import uuid4

import pytest

from app import create_app
from app.services.excute_testcases import TestTaskManager
from app.services.task_report import (
    build_report_results,
    build_report_stats,
    generate_task_report,
)
from utils.task_state import TaskStatus
from TestRunner.core.Base import StepStatus, TestStatus


@pytest.fixture
def task_manager():
    previous_instance = TestTaskManager._instance
    TestTaskManager._instance = None
    manager = TestTaskManager()
    yield manager
    manager._tasks.clear()
    TestTaskManager._instance = previous_instance


@pytest.fixture
def app_with_report_dir(tmp_path):
    return create_app(
        test_config={"TESTING": True, "TASK_REPORTS_DIR": str(tmp_path)},
        project_config={
            "TestBed": {},
            "TestSet": {"test_cases": []},
            "base_dir": str(tmp_path),
        },
    )


def _sample_details():
    return {
        "status": "失败",
        "progress": {
            "case_stats": {
                "total_cases": 2,
                "passed": 1,
                "failed": 1,
                "error": 0,
                "skipped": 0,
            }
        },
        "test_cases": [
            {
                "test_class_name": "unsafe_case",
                "test_instance_name": "<script>alert(1)</script>",
                "test_status": "失败",
                "duration": 0.125,
                "error": "case error: <b>unsafe</b>",
                "steps": [
                    {
                        "name": "<img src=x onerror=alert(1)>",
                        "status": "失败",
                        "error": "step error: <svg onload=alert(2)>",
                    },
                    {
                        "name": "skipped step",
                        "status": "跳过",
                        "skip_reason": "previous step failed",
                    },
                ],
            },
            {
                "test_class_name": "passing_case",
                "test_instance_name": "passing case",
                "test_status": "通过",
                "duration": 0.25,
                "steps": [{"name": "successful step", "status": "通过"}],
            },
        ],
    }


def test_report_adapter_normalizes_chinese_statuses_and_statistics():
    details = _sample_details()

    results = build_report_results(details)
    stats = build_report_stats(details)

    assert results[0]["status"] == TestStatus.FAIL
    assert results[0]["steps"][0]["status"] == StepStatus.FAIL
    assert results[0]["steps"][1]["status"] == StepStatus.SKIP
    assert results[1]["status"] == TestStatus.PASS
    assert stats == {
        "total": 2,
        "passed": 1,
        "failed": 1,
        "error": 0,
        "skipped": 0,
    }


def test_report_generation_escapes_dynamic_text_and_uses_status_css(tmp_path):
    task_id = str(uuid4())
    details = _sample_details()

    report_path = generate_task_report(
        task_id,
        details,
        runner_stats={"total": 2, "passed": 1, "failed": 1, "error": 0, "skipped": 0},
        report_dir=tmp_path,
    )
    html = report_path.read_text(encoding="utf-8")

    assert report_path == (tmp_path / f"{task_id}.html").resolve()
    assert 'class="status-fail"' in html
    assert 'class="step-fail"' in html
    assert 'class="step-skip"' in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "&lt;img src=x onerror=alert(1)&gt;" in html
    assert "&lt;svg onload=alert(2)&gt;" in html
    assert "&lt;b&gt;unsafe&lt;/b&gt;" in html
    assert "<script>alert(1)</script>" not in html
    assert "<img src=x onerror=alert(1)>" not in html
    assert "通过：1" in html
    assert "失败：1" in html


def test_generate_task_report_rejects_path_like_task_ids(tmp_path):
    with pytest.raises(ValueError, match="无效的任务 ID"):
        generate_task_report("../outside", _sample_details(), report_dir=tmp_path)

    assert not (tmp_path.parent / "outside.html").exists()


def test_report_download_api_returns_file_and_status_link(
    task_manager, app_with_report_dir, tmp_path
):
    task_id = task_manager.create_task({})
    task = task_manager.get_task(task_id)
    task.transition(TaskStatus.RUNNING)
    task.transition(TaskStatus.COMPLETED)

    report_path = tmp_path / f"{task_id}.html"
    report_path.write_text("<h1>Task report</h1>", encoding="utf-8")
    task.set_report_path(report_path)

    client = app_with_report_dir.test_client()
    status_response = client.get(f"/huixin/getTaskStatus/{task_id}")
    assert status_response.status_code == 200
    status_payload = status_response.get_json()["data"]
    assert status_payload["report_available"] is True
    assert status_payload["report_url"] == f"/huixin/getTaskReport/{task_id}"
    assert status_payload["report_error"] is None

    response = client.get(status_payload["report_url"])
    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert f"autotest-report-{task_id}.html" in response.headers["Content-Disposition"]
    assert response.get_data(as_text=True) == "<h1>Task report</h1>"


def test_report_download_api_returns_explicit_errors_for_unavailable_reports(
    task_manager, app_with_report_dir
):
    client = app_with_report_dir.test_client()

    missing_task_response = client.get("/huixin/getTaskReport/not-a-task")
    assert missing_task_response.status_code == 404

    running_id = task_manager.create_task({})
    task_manager.get_task(running_id).transition(TaskStatus.RUNNING)
    running_response = client.get(f"/huixin/getTaskReport/{running_id}")
    assert running_response.status_code == 409

    failed_report_id = task_manager.create_task({})
    failed_report = task_manager.get_task(failed_report_id)
    failed_report.transition(TaskStatus.RUNNING)
    failed_report.set_report_error("HTML 报告生成失败")
    failed_report.transition(TaskStatus.ERROR, error="测试执行异常")
    failed_response = client.get(f"/huixin/getTaskReport/{failed_report_id}")
    assert failed_response.status_code == 500
    assert failed_response.get_json()["message"] == "测试报告生成失败"


def test_expired_task_cleanup_removes_its_generated_report(task_manager, tmp_path):
    task_id = task_manager.create_task({})
    task = task_manager.get_task(task_id)
    task.transition(TaskStatus.RUNNING)
    task.transition(TaskStatus.COMPLETED)
    report_path = tmp_path / f"{task_id}.html"
    report_path.write_text("expired report", encoding="utf-8")
    task.set_report_path(report_path)
    task.end_time = task.end_time.replace(year=task.end_time.year - 1)

    task_manager._cleanup_expired_tasks(max_keep_time=3600)

    assert task_manager.get_task(task_id) is None
    assert not report_path.exists()
