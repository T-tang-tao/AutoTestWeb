"""Happy-path product lookup against the local Mock API."""

import requests

from TestRunner.core.Base import Base


case_name = "Mock API：查询商品成功"


class product_success(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.params = kwargs.get("params") or {}
        self.base_url = self.params["base_url"].rstrip("/")
        self.response = None
        self.payload = None

    def defineSteps(self):
        self.def_step("请求已存在商品", self.request_product)
        self.def_step("校验商品响应字段", self.assert_product)

    def request_product(self):
        self.response = requests.get(
            f"{self.base_url}/api/products/1",
            timeout=3,
        )
        self.payload = self.response.json()

    def assert_product(self):
        assert self.response.status_code == 200
        assert self.payload["code"] == "OK"
        assert self.payload["data"]["id"] == 1
        assert self.payload["data"]["name"] == "Demo Product"
        assert self.payload["data"]["price"] == 19.9

    def tearDown(self):
        self.response = None
