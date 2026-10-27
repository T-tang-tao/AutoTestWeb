"""Parameter-validation failure scenario against the local Mock API."""

import requests

from TestRunner.core.Base import Base


case_name = "Mock API：参数校验失败"


class validation_error(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.params = kwargs.get("params") or {}
        self.base_url = self.params["base_url"].rstrip("/")
        self.response = None
        self.payload = None

    def defineSteps(self):
        self.def_step("提交无效订单参数", self.submit_invalid_order)
        self.def_step("校验 400 和字段错误", self.assert_validation_error)

    def submit_invalid_order(self):
        self.response = requests.post(
            f"{self.base_url}/api/orders",
            json={"quantity": 0},
            timeout=3,
        )
        self.payload = self.response.json()

    def assert_validation_error(self):
        assert self.response.status_code == 400
        assert self.payload["code"] == "VALIDATION_ERROR"
        assert "product_id" in self.payload["errors"]
        assert "quantity" in self.payload["errors"]

    def tearDown(self):
        self.response = None
