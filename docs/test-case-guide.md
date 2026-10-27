# 自动化测试用例编写指南

本文适用于 `TestRunner` 目录约定的 Python 用例。现有执行器会动态加载用例文件、创建实例、调用 `defineSteps()` 注册的步骤，再执行每个步骤并汇总用例/步骤状态。

## 1. 用例文件与目录

推荐把新用例放在业务对应目录下，并在 `TestSet.test_cases` 中用相对于 `base_dir` 的路径引用，例如：

```text
examples/mock_api/
├── config.example.yml
└── test_cases/
    └── product_success.py
```

文件名、用例类名必须一致（区分大小写）。例如 `product_success.py` 中定义 `class product_success(Base)`。可以在模块顶部定义字符串常量 `case_name`，用于结果展示。

## 2. 最小用例模板

下面示例来自项目的 Mock API 演示的简化结构：

```python
import requests

from TestRunner.core.Base import Base


case_name = "查询商品成功"


class product_success(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        params = kwargs.get("params") or {}
        self.base_url = params["base_url"].rstrip("/")
        self.response = None
        self.payload = None

    def setUp(self):
        # 可选：执行用例前置准备
        pass

    def defineSteps(self):
        # 这里只登记步骤，不应在此处执行请求或断言
        self.def_step("请求商品详情", self.request_product)
        self.def_step("校验响应数据", self.assert_product)

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

    def tearDown(self):
        # 用于成功路径的轻量清理
        self.response = None
```

执行器会向用例构造函数传入 `user_cookie`；当 `TestRunner(..., params=...)` 传入了非空参数字典时，也会传入 `params`。用例可用 `kwargs.get("params") or {}` 安全读取可选参数。若用例不需要自定义构造函数，直接继承 `Base` 即可。

`defineSteps()` 通过 `self.def_step(name, method, args=None, kwargs=None)` 注册步骤。请求、解析、断言等实际操作应该放在步骤方法里，而不是在 `defineSteps()` 里提前执行。

## 3. TestBed、TestSet 与执行参数

最小 Mock API 配置示例：

```yaml
TestBed:
  env: mock-api
  HuiXin:
    host: http://127.0.0.1
    users: {}

TestSet:
  test_cases:
    - path: test_cases/product_success.py

base_dir: .
```

配置必须包含 `TestBed`、`TestSet` 和 `base_dir`。TestRunner 也会读取 `TestBed.HuiXin.users` 以初始化登录信息；非真实业务用例应使用空用户列表/字典和本地 Mock API，避免触发真实登录请求。用例路径按 `base_dir / path` 解析。

自定义参数在创建执行器时单独传入：

```python
from TestRunner.core.TestRunner import TestRunner

runner = TestRunner(config, params={"base_url": "http://127.0.0.1:5010"})
runner.run()
```

仓库已提供可直接运行的样例：`python examples/mock_api/run_demo.py`。其配置、用例和运行方法见 [Mock API 演示指南](mock-api-demo.md)。

## 4. 步骤设计建议

优先把一个步骤写成一个清晰动作或一组紧密相关的断言。常见顺序是“准备请求 → 执行请求 → 校验状态码/业务码 → 校验关键字段”。对预期的业务错误，要断言它的业务错误码和结构；不要把“收到错误响应”本身当作测试失败。

所有 HTTP 请求都设置明确的 `timeout`。对预期返回 4xx 的场景，使用不会自动因状态码抛出异常的客户端调用方式，然后断言状态码；项目 `HttpClient.get()` 当前会调用 `raise_for_status()`，更适合预期是成功状态码的请求。

不要依赖固定长时间 `sleep` 来等待业务完成。只在专门验证延迟/超时行为时使用可控延迟；优先通过响应、状态轮询或明确的等待条件判定结果。

## 5. 状态与失败策略

- 所有步骤通过后，用例状态为 `通过`。
- 断言失败时，用例状态为 `失败`，失败步骤保留错误信息，后续步骤标记为 `跳过`。
- 非断言异常（例如请求连接失败或代码异常）会将用例状态标记为 `错误`。
- 步骤的 `status` 与用例的 `test_status` 会进入结果报告；检查关键业务结果时不要只断言 HTTP 状态，还应断言业务数据。

**当前执行器的清理限制：** 用例主体步骤发生断言失败/异常时，现有主流程不会自动调用该用例的 `tearDown()`。因此，不能把关键资源释放、数据库清理或撤销测试数据完全寄托在 `tearDown()` 上。避免在步骤中创建不受管理的持久资源；涉及数据库连接时，遵循 [数据库客户端事务与清理约定](database-client.md)。这一限制应在独立的执行生命周期修复中处理。

## 6. 测试数据和外部依赖

- 自动化测试应默认指向 Mock API 或专用测试环境，不要把生产服务地址、真实用户名/密码、Cookie 或本地个人配置提交到仓库。
- 对写入型接口使用专用、可辨识的测试数据；明确记录测试后清理责任。多条相关数据库写入使用显式事务，并按 [数据库客户端说明](database-client.md) 管理连接。
- 为外部 HTTP 调用设置超时；不要依赖个人电脑上的服务一定启动。
- 用 fake/mock 隔离不属于当前测试目标的外部依赖。若目标是检查业务 API，不应让数据库、账号登录或其他服务故障掩盖 API 断言。
- 测试用例应能在隔离环境中重复运行，避免依赖上一条用例写入的隐式状态。

## 7. 验证与排查

运行 Mock API 演示的端到端测试：

```bash
python -m pytest -q tests/test_mock_api_demo.py
python examples/mock_api/run_demo.py
```

新增或修改用例后，先检查用例文件名/类名是否完全一致、配置路径是否相对 `base_dir` 正确、`defineSteps()` 是否仅登记步骤、HTTP 请求是否有 timeout，以及断言是否同时覆盖协议状态和业务响应。
