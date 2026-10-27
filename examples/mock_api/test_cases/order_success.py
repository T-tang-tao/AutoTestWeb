"""Happy-path order submission against the local Mock API."""

import requests

from TestRunner.core.Base import Base


case_name = "Mock API：创建订单成功"


class order_success(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.params = kwargs.get("params") or {}
        self.base_url = self.params["base_url"].rstrip("/")
        self.response = None
        self.payload = None

    def defineSteps(self):
        self.def_step("提交有效订单", self.submit_order)
        self.def_step("校验订单创建结果", self.assert_order)

    def submit_order(self):
        self.response = requests.post(
            f"{self.base_url}/api/orders",
            json={"product_id": 1, "quantity": 2},
            timeout=3,
        )
        self.payload = self.response.json()

    def assert_order(self):
        assert self.response.status_code == 201
        assert self.payload["code"] == "ORDER_CREATED"
        assert self.payload["data"]["product_id"] == 1
        assert self.payload["data"]["quantity"] == 2

    def tearDown(self):
        self.response = None
