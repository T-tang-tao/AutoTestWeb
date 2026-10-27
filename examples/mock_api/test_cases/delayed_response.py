"""Controllable delay scenario against the local Mock API."""

import requests

from TestRunner.core.Base import Base


case_name = "Mock API：可控延迟响应"


class delayed_response(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.params = kwargs.get("params") or {}
        self.base_url = self.params["base_url"].rstrip("/")
        self.response = None
        self.payload = None

    def defineSteps(self):
        self.def_step("请求延迟 0.08 秒的接口", self.request_delayed_endpoint)
        self.def_step("校验延迟参数和响应", self.assert_delay)

    def request_delayed_endpoint(self):
        self.response = requests.get(
            f"{self.base_url}/api/delay",
            params={"seconds": 0.08},
            timeout=3,
        )
        self.payload = self.response.json()

    def assert_delay(self):
        assert self.response.status_code == 200
        assert self.payload["code"] == "OK"
        assert self.payload["requested_delay"] == 0.08
        assert self.payload["actual_delay"] >= 0.08

    def tearDown(self):
        self.response = None
