"""Backward-compatible routes for the legacy HuiXin integration."""

from flask import Blueprint, request

from app.services.huixin_testcases import get_huixin_test_cases
from app.routes.api_routes import (
    download_task_report_file,
    read_task_status,
    read_test_bed_config,
    save_test_bed_config,
    submit_test_cases,
)
from utils.response import APIError, api_response

huixin_bp = Blueprint("huixin", __name__)


@huixin_bp.route("/getConfig", methods=["GET"])
@api_response
def get_config():
    """Legacy alias for reading the TestBed configuration."""
    return read_test_bed_config()


@huixin_bp.route("/saveConfig", methods=["POST"])
@api_response
def save_config_route():
    """Legacy save endpoint, including the old HuiXin-specific ID convention."""
    config_data = request.get_json(silent=True)
    if not isinstance(config_data, dict) or not config_data:
        raise APIError("请求体必须是非空的 JSON 对象", status_code=400)

    huixin = config_data.get("HuiXin")
    users = huixin.get("users") if isinstance(huixin, dict) else None
    criminal = users.get("criminal") if isinstance(users, dict) else None
    if isinstance(criminal, dict) and criminal.get("username"):
        criminal["id"] = criminal["username"]

    result = save_test_bed_config(config_data)
    return result, "配置保存成功", 200


@huixin_bp.route("/executeTestCases", methods=["POST"])
@api_response
def start_test():
    """Legacy assessment-based task submission; new clients should use POST /api/v1/tasks."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise APIError("请求体必须是 JSON 对象", status_code=400)

    params = payload.get("params", {})
    if params is None:
        params = {}
    if not isinstance(params, dict):
        raise APIError("params 必须是 JSON 对象", status_code=400)

    test_cases = get_huixin_test_cases(payload)
    if not test_cases:
        raise APIError("assessment 缺失或不支持，未找到对应测试用例", status_code=400)

    return submit_test_cases(
        test_cases,
        params,
        status_code=200,
        message="任务已启动",
    )


@huixin_bp.route("/getTaskStatus/<task_id>", methods=["GET"])
@api_response
def get_task_status(task_id: str):
    """Legacy task-status route retained for existing HuiXin clients."""
    return read_task_status(task_id, generic=False)


@huixin_bp.route("/getTaskReport/<task_id>", methods=["GET"])
@api_response
def get_task_report(task_id: str):
    """Legacy report-download route retained for existing HuiXin clients."""
    return download_task_report_file(task_id)


@huixin_bp.route("/createReport", methods=["POST"])
@api_response
def create_report():
    """Submit the business-specific PrisonAssessmentSystem report case."""
    data = request.get_json(silent=True) or {}
    case = [{
        "path": "PrisonAssessmentSystem/TestCases/Assessment/Tools/create_report.py",
        "name": "create_report",
    }]
    return submit_test_cases(
        case,
        data,
        status_code=200,
        message="任务已启动",
    )
