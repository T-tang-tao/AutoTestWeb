"""Expected business-level error response against the local Mock API."""

import requests

from TestRunner.core.Base import Base


case_name = "Mock API：业务错误码"


class business_error(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.params = kwargs.get("params") or {}
        self.base_url = self.params["base_url"].rstrip("/")
        self.response = None
        self.payload = None

    def defineSteps(self):
        self.def_step("请求不存在的商品", self.request_missing_product)
        self.def_step("校验业务错误码", self.assert_business_error)

    def request_missing_product(self):
        self.response = requests.get(
            f"{self.base_url}/api/products/999",
            timeout=3,
        )
        self.payload = self.response.json()

    def assert_business_error(self):
        assert self.response.status_code == 200
        assert self.payload["code"] == "PRODUCT_NOT_FOUND"
        assert self.payload["data"] is None
        assert "不存在" in self.payload["message"]

    def tearDown(self):
        self.response = None
