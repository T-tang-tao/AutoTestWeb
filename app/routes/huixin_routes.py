from copy import deepcopy

from flask import Blueprint, current_app, request, send_file

from app.services.excute_testcases import TestTaskManager, submit_test_task, execute_test_task
from utils.response import api_response, APIError
from utils.task_state import TERMINAL_TASK_STATUSES

huixin_bp = Blueprint('huixin', __name__)

def _config_loader():
    return current_app.extensions["config_loader"]


@huixin_bp.route('/getConfig', methods=['GET'])
@api_response
def get_config():
    config = _config_loader().get_config()['TestBed']
    if not config:
        raise APIError("未找到配置数据", status_code=500)
    return config


@huixin_bp.route('/saveConfig', methods=['POST'])
@api_response
def save_config_route():
    config_data = request.json
    config_data['HuiXin']['users']['criminal']['id'] = config_data['HuiXin']['users']['criminal']['username']
    if not config_data:
        raise APIError("请求体为空", status_code=400)
    return _config_loader().save_test_bed(test_bed_data=config_data), "配置保存成功", 200


# 执行评估用例
@huixin_bp.route('/executeTestCases', methods=['POST'])
@api_response
def start_test():
    """启动测试任务"""
    assessment_config = request.json
    params = assessment_config['params']
    test_cases = execute_test_task(assessment_config)
    if not test_cases:
        raise APIError("缺少测试用例配置", 500)

    # 每个任务使用独立配置副本，避免并发请求互相覆盖测试用例。
    config = deepcopy(_config_loader().config)
    config['TestSet']['test_cases'] = test_cases
    task_id = submit_test_task(
        config, params, report_dir=current_app.config.get("TASK_REPORTS_DIR")
    )

    return {"task_id": task_id, "status": TestTaskManager().get_task(task_id).status}, "任务已启动"


@huixin_bp.route('/getTaskStatus/<task_id>', methods=['GET'])
@api_response
def get_task_status(task_id: str):
    """查询任务状态（含步骤级详情）"""
    task = TestTaskManager().get_task(task_id)
    if not task:
        raise APIError({"error": "任务不存在或已过期"}, 404)
    return task.to_dict()


@huixin_bp.route('/getTaskReport/<task_id>', methods=['GET'])
@api_response
def get_task_report(task_id: str):
    """Download a task's generated HTML report."""
    task = TestTaskManager().get_task(task_id)
    if not task:
        raise APIError("任务不存在或已过期", 404)

    terminal_states = {status.value for status in TERMINAL_TASK_STATUSES}
    if task.status not in terminal_states:
        raise APIError("任务尚未结束，报告暂不可下载", 409)

    report_path = task.get_report_path()
    if report_path is None or not report_path.is_file():
        if task.report_error:
            raise APIError("测试报告生成失败", 500)
        raise APIError("测试报告不存在或已过期", 404)

    return send_file(
        report_path,
        mimetype="text/html",
        as_attachment=True,
        download_name=f"autotest-report-{task.task_id}.html",
    )


@huixin_bp.route('/createReport', methods=['POST'])
@api_response
def create_report():
    """查询任务状态（含步骤级详情）"""
    data = request.json
    case = [{
        'path': 'PrisonAssessmentSystem/TestCases/Assessment/Tools/create_report.py',
        'name': 'create_report',

    }]
    # 报告任务也走统一提交入口，并使用独立配置副本。
    config = deepcopy(_config_loader().config)
    config['TestSet']['test_cases'] = case
    task_id = submit_test_task(
        config, data, report_dir=current_app.config.get("TASK_REPORTS_DIR")
    )

    return {"task_id": task_id, "status": TestTaskManager().get_task(task_id).status}, "任务已启动"
#
# @app.route('/api/tests/<task_id>/cancel', methods=['POST'])
# def cancel_test(task_id):
#     """取消测试任务（需 TestRunner 支持中断）"""
#     task = test_tasks.get(task_id)
#     if not task:
#         return jsonify({"error": "Task not found"}), 404
#
#     if task.status in ["completed", "failed", "cancelled"]:
#         return jsonify({"status": task.status, "message": "Task already finished"})
#
#     task.status = "cancelled"
#     return jsonify({"status": "cancelling", "message": "Cancellation request sent"})
