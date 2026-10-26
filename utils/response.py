from functools import wraps
from typing import Any

from flask import jsonify, request, Response
from utils.LoggerManager import LoggerManager

logger = LoggerManager().get_logger()


# 统一响应格式（简化版）
class APIResponse:
    @staticmethod
    def success(data: Any = None, message: str = "", status_code: int = 200) -> tuple:
        """统一成功响应，自动处理数据序列化"""
        # 序列化前置处理：将非可序列化对象转为字典
        serialized_data = APIResponse._serialize_data(data)

        return jsonify({
            "status": "success",
            "message": message,
            "data": serialized_data
        }), status_code

    @staticmethod
    def _serialize_data(data: Any) -> Any:
        """递归处理数据序列化，支持自定义对象（需实现to_dict方法）"""
        if data is None:
            return None

        # 1. 处理列表/元组：递归序列化每个元素
        if isinstance(data, (list, tuple)):
            return [APIResponse._serialize_data(item) for item in data]

        # 2. 处理字典：递归序列化每个值
        if isinstance(data, dict):
            return {k: APIResponse._serialize_data(v) for k, v in data.items()}

        # 3. 处理自定义对象：如果有to_dict方法，调用转换
        if hasattr(data, "to_dict") and callable(data.to_dict):
            return APIResponse._serialize_data(data.to_dict())  # 递归处理转换后的字典

        # 4. 处理其他基础类型（str/int/float/bool等）：直接返回
        if isinstance(data, (str, int, float, bool, type(None))):
            return data

        # 5. 未处理的类型：转为字符串（避免报错，可根据需求调整）
        return str(data)

    @staticmethod
    def error(message="操作失败", status_code=400, data=None):
        return jsonify({
            "status": "error",
            "message": message,
            "data": data
        }), status_code


# 自定义异常（保留必要类型）
class APIError(Exception):
    def __init__(self, message, status_code=500, data=None):
        self.message = message
        self.status_code = status_code
        self.data = data
        super().__init__(message)


# 简化版响应装饰器
def api_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 记录请求开始
        path = request.path
        logger.info(f"请求开始: {request.method} {path}")

        try:
            result = func(*args, **kwargs)

            # 1. 若直接返回Response，直接返回（避免二次处理）
            if isinstance(result, Response):
                logger.debug(f"直接返回Response对象: {path}")
                return result

            # 2. 解析返回值（支持单值/元组格式）
            data, msg, code = result, "", 200
            if isinstance(result, tuple):
                data = result[0] if len(result) >= 1 else None
                msg = result[1] if len(result) >= 2 else ""
                code = result[2] if len(result) >= 3 else 200

            # 3. 检查data是否为Response（防止嵌套）
            if isinstance(data, Response):
                raise ValueError("数据中包含Response对象，无法序列化")

            # 4. 正常返回成功响应
            return APIResponse.success(data, msg, code)

        except APIError as e:
            logger.error(f"API错误: {e.message} ({e.status_code})")
            return APIResponse.error(e.message, e.status_code, e.data)
        except Exception as e:
            logger.error(f"服务器错误: {str(e)}", exc_info=True)
            return APIResponse.error("服务器内部错误", 500)
        finally:
            logger.info(f"请求结束: {request.method} {path}")

    return wrapper
