import requests

from utils.LoggerManager import LoggerManager


def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            # 尝试执行被装饰的函数
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            # 捕获异常并记录日志
            self = args[0]  # 获取实例对象
            self._record_exception(e)
            return None  # 返回 None 作为默认值

    return wrapper


class HttpClient:
    def __init__(self, **kwargs):
        self.default_timeout = kwargs.get("timeout", 10)
        self.headers = {
            "login_type": "mg",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh,en;q=0.9,en-US;q=0.8",
            "Connection": "keep-alive",
            "Cookie": "",
            "Content-Type": "application/json; charset=UTF-8"
        }
        self.session = requests.Session()
        self.last_request = None
        self.last_response = None
        self.logger = LoggerManager().get_logger()
        self.cookies = None

    def __del__(self):
        self.session.close()

    def _merge_headers(self, headers):
        """合并默认 headers 和自定义 headers"""
        return {**self.headers, **(headers or {})}

    def set_global_timeout(self, timeout):
        """设置全局超时时间（秒）"""
        self.default_timeout = timeout

    def set_global_headers(self, headers):
        """更新全局请求头"""
        self.headers.update(headers)

    def set_cookies(self, cookies: str):
        """设置全局 cookies"""
        self.headers.update({"Cookie": cookies})

    @error_handler
    def get(self, url, params=None, **kwargs):
        """GET 请求"""
        kwargs.setdefault('timeout', self.default_timeout)
        headers = self._merge_headers(kwargs.pop('headers', None))

        self._record_request('GET', url, params=params, **kwargs)
        response = self.session.get(
            url,
            headers=headers,
            params=params,
            **kwargs
        )
        response.raise_for_status()  # 检查响应状态码，如果不是 200 会抛出异常
        self._record_response(response)
        return response

    @error_handler
    def post(self, url, json=None, data=None, content_type="", **kwargs):
        """POST 请求"""
        kwargs.setdefault('timeout', self.default_timeout)

        # 动态设置 Content-Type
        if data:
            self.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        if json:
            self.headers['Content-Type'] = 'application/json; charset=UTF-8'

        self._record_request('POST', url, data=data, json=json, **kwargs)
        res = self.session.post(
            url,
            json=json,
            data=data,
            headers=self.headers,
            **kwargs
        )
        # res.raise_for_status()  # 检查响应状态码，如果不是 200 会抛出异常
        self._record_response(res)
        return res

    def _record_request(self, method: str, url: str, **kwargs):
        """记录请求信息用于测试验证"""
        self.last_request = {
            'method': method,
            'url': url,
            'params': kwargs.get('params'),
            'data': kwargs.get('data'),
            'json': kwargs.get('json'),
            'headers': self._merge_headers(kwargs.get('headers'))
        }
        self.logger.debug(
            f"request - method: {method} -- url: {url}, \nparams: {kwargs.get('params')}, "
            f"\nheaders: {self.last_request['headers']}  \ndata: {kwargs.get('data')}, \nJSON: {kwargs.get('json')}, "
        )

    def _record_response(self, response):
        """记录响应信息"""
        self.last_response = {
            'status_code': response.status_code,
            'json': response.content
        }
        self.logger.debug(
            f"response - status_code: {response.status_code}, content: {response.content or response.text}"
        )

    def _record_exception(self, exception):
        """记录异常信息"""
        self.logger.error(
            f"request failed - error msg: {str(exception)}"
        )
        raise AssertionError(f"request failed - error msg: {str(exception)}")

    def reset(self):
        """重置实例状态保证测试隔离性"""
        self.session.close()
        self.session = requests.Session()
        self.last_request = None
        self.last_response = None
