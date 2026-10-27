from pathlib import Path

from flask import Blueprint, request

from app.services.load_testsets import traverse_test_cases
from utils.response import api_response, APIError

base_bp = Blueprint('base', __name__)


@base_bp.route('/', methods=['GET'])
@api_response
def home():
    return {"message": "AutoTestWeb API Server is running", "version": "1.0"}, 200


@base_bp.route('/getTestCases', methods=['GET'])
@api_response
def get_config():
    # Business目录路径
    business_dir = Path(__file__).resolve().parents[2] / "Business"
    # 获取测试用例数据
    test_cases_data = traverse_test_cases(business_dir)
    # 转换为JSON
    return test_cases_data, 200
