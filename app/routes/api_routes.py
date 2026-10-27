"""Versioned, business-agnostic API routes for AutoTestWeb."""

from copy import deepcopy
from pathlib import Path, PurePosixPath, PureWindowsPath

from flask import Blueprint, current_app, request, send_file, url_for

from app.services.excute_testcases import TestTaskManager, submit_test_task
from app.services.load_testsets import traverse_test_cases
from utils.response import APIError, api_response
from utils.task_state import TERMINAL_TASK_STATUSES

api_bp = Blueprint("api", __name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _config_loader():
    return current_app.extensions["config_loader"]


def read_test_bed_config():
    """Return the configured TestBed without assuming a specific business schema."""
    config = _config_loader().get_config().get("TestBed")
    if not config:
        raise APIError("未找到测试环境配置", status_code=404)
    return config


def save_test_bed_config(config_data):
    """Persist a TestBed payload without applying business-specific transformations."""
    if not isinstance(config_data, dict) or not config_data:
        raise APIError("请求体必须是非空的 JSON 对象", status_code=400)
    return _config_loader().save_test_bed(test_bed_data=config_data)


def _validate_test_cases(test_cases):
    if not isinstance(test_cases, list) or not test_cases:
        raise APIError("test_cases 必须是非空数组", status_code=400)

    normalized = []
    for index, case in enumerate(test_cases):
        if not isinstance(case, dict):
            raise APIError(f"test_cases[{index}] 必须是对象", status_code=400)

        raw_path = case.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise APIError(
                f"test_cases[{index}].path 必须是非空相对路径",
                status_code=400,
            )

        path_text = raw_path.strip().replace("\\", "/")
        relative_path = PurePosixPath(path_text)
        if (
            relative_path.is_absolute()
            or PureWindowsPath(raw_path).is_absolute()
            or ".." in relative_path.parts
            or not relative_path.suffix == ".py"
        ):
            raise APIError(
                f"test_cases[{index}].path 必须是仓库业务目录下的 Python 相对路径",
                status_code=400,
            )

        name = case.get("name") or relative_path.stem
        if not isinstance(name, str) or not name.strip():
            raise APIError(
                f"test_cases[{index}].name 必须是非空字符串",
                status_code=400,
            )

        normalized.append({"path": path_text, "name": name.strip()})

    return normalized


def submit_test_cases(test_cases, params=None, status_code=202, message="测试任务已接受"):
    """Submit an explicit case list through the shared background task service."""
    normalized_cases = _validate_test_cases(test_cases)
    if params is None:
        params = {}
    if not isinstance(params, dict):
        raise APIError("params 必须是 JSON 对象", status_code=400)

    config = deepcopy(_config_loader().config)
    config.setdefault("TestSet", {})["test_cases"] = normalized_cases
    task_id = submit_test_task(
        config,
        params,
        report_dir=current_app.config.get("TASK_REPORTS_DIR"),
    )
    task = TestTaskManager().get_task(task_id)
    status = task.status if task is not None else "pending"
    return {"task_id": task_id, "status": status}, message, status_code


def read_task_status(task_id, generic=False):
    task = TestTaskManager().get_task(task_id)
    if not task:
        raise APIError("任务不存在或已过期", status_code=404)

    payload = task.to_dict()
    if generic and payload.get("report_available"):
        payload["report_url"] = url_for("api.get_task_report", task_id=task_id)
    return payload


def download_task_report_file(task_id):
    task = TestTaskManager().get_task(task_id)
    if not task:
        raise APIError("任务不存在或已过期", status_code=404)

    terminal_states = {status.value for status in TERMINAL_TASK_STATUSES}
    if task.status not in terminal_states:
        raise APIError("任务尚未结束，报告暂不可下载", status_code=409)

    report_path = task.get_report_path()
    if report_path is None or not report_path.is_file():
        if task.report_error:
            raise APIError("测试报告生成失败", status_code=500)
        raise APIError("测试报告不存在或已过期", status_code=404)

    return send_file(
        report_path,
        mimetype="text/html",
        as_attachment=True,
        download_name=f"autotest-report-{task.task_id}.html",
    )


def _configured_business_root():
    config = _config_loader().get_config()
    configured_root = config.get("base_dir")
    if configured_root:
        root = Path(configured_root).expanduser()
        if root.is_absolute():
            return root.resolve()
        candidates = [
            (PROJECT_ROOT / root).resolve(),
            (PROJECT_ROOT / "configs" / root).resolve(),
        ]
        for candidate in candidates:
            if candidate.is_dir():
                return candidate
    return PROJECT_ROOT / "Business"


def _make_paths_relative(items, root):
    for item in items:
        path = Path(item["path"])
        try:
            item["path"] = path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            item["path"] = path.as_posix()
        _make_paths_relative(item.get("children", []), root)
    return items


@api_bp.route("/config/test-bed", methods=["GET"])
@api_response
def get_test_bed():
    """Read the current TestBed configuration."""
    return read_test_bed_config()


@api_bp.route("/config/test-bed", methods=["PUT"])
@api_response
def update_test_bed():
    """Replace the current TestBed configuration."""
    config_data = request.get_json(silent=True)
    result = save_test_bed_config(config_data)
    return result, "测试环境配置保存成功", 200


@api_bp.route("/test-cases", methods=["GET"])
@api_response
def list_test_cases():
    """List available cases using paths relative to the configured business root."""
    root = _configured_business_root()
    items = traverse_test_cases(str(root))
    return _make_paths_relative(items, root)


@api_bp.route("/tasks", methods=["POST"])
@api_response
def create_task():
    """Submit a task using an explicit test_cases list and optional params."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise APIError("请求体必须是 JSON 对象", status_code=400)
    return submit_test_cases(payload.get("test_cases"), payload.get("params"))


@api_bp.route("/tasks/<task_id>", methods=["GET"])
@api_response
def get_task(task_id):
    """Return task status and the execution result snapshot."""
    return read_task_status(task_id, generic=True)


@api_bp.route("/tasks/<task_id>/report", methods=["GET"])
@api_response
def get_task_report(task_id):
    """Download the HTML report for a completed task."""
    return download_task_report_file(task_id)
