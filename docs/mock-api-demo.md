# Mock API 本地演示

此示例使用仓库自带的 Flask Mock API、真实的 `TestRunner` 与进程内任务服务演示自动化测试主链路。它不需要生产/内网业务服务、真实账号、个人本地 YAML 或 MySQL。

## 一条命令运行

先安装项目与开发测试依赖：

```bash
python -m pip install -r requirements-dev.txt
python examples/mock_api/run_demo.py
```

未传入 `--base-url` 时，脚本会在回环地址 `127.0.0.1` 上临时启动一个端口由操作系统分配的 Mock API，加载 `config.example.yml`，并通过实际的 `submit_test_task()` 后台任务入口运行示例测试套；结束后会关闭临时服务。命令会把任务级状态、测试套状态、耗时、统计、各用例/步骤结果和 HTML 报告路径以 JSON 打印到控制台。成功时任务状态为 `completed`、测试套状态为 `通过`，进程退出码为 0；如果有用例失败或异常，退出码为 1。

该命令会真正执行任务注册、状态转换、TestRunner 的用例加载、步骤定义、逐步调用、断言、结果快照和资源清理，并通过本机 HTTP 请求访问 Mock API，而不是只使用 Flask test client 模拟执行器流程。

默认报告路径为 `reports/mock-api-demo-report.html`；通过 `--report-path <path>` 可指定其他位置。报告从任务完成后缓存的 JSON-safe 结果快照生成，不会依赖已释放的 Runner 实例。

## 独立启动 Mock API

也可以把示例服务单独运行在固定端口。终端一执行：

Windows PowerShell：

```powershell
$env:MOCK_API_HOST = "127.0.0.1"
$env:MOCK_API_PORT = "5010"
python examples/mock_api/server.py
```

macOS / Linux：

```bash
MOCK_API_HOST=127.0.0.1 MOCK_API_PORT=5010 python examples/mock_api/server.py
```

终端二运行 TestRunner：

```bash
python examples/mock_api/run_demo.py --base-url http://127.0.0.1:5010
```

`--base-url` 也可以通过环境变量 `MOCK_API_BASE_URL` 指定。启动后可以先访问 `http://127.0.0.1:5010/health` 确认服务正常。

## 实际运行结果与报告

下面的摘要来自真实的 GitHub Actions 执行，不是手工伪造的结果：

- [实际运行记录 #40455785051](https://github.com/T-tang-tao/AutoTestWeb/actions/runs/40455785051)：Python 3.10、3.11、3.12 均运行全量 pytest、Mock API Demo 以及 HTML 报告生成；其中 Python 3.12 的输出记录到任务状态为 `completed`、测试套状态为 `通过`、5 个用例全部通过。
- 每个 Python 版本都上传了名为 `mock-api-report-python-3.10`、`mock-api-report-python-3.11` 或 `mock-api-report-python-3.12` 的 HTML 报告 artifact。打开上述运行记录页面可下载报告 artifact；按当前工作流配置保留 14 天。
- README 中的 [运行结果摘要图](../docs/images/mock-api-demo-result.svg) 是基于同次真实运行输出整理的可视化摘要；它与 workflow 日志及可下载 HTML 报告相互核验。

运行命令的结果 JSON 同时区分两套状态：任务状态 `task_status=completed`，测试套状态 `status=通过`。这两个值语义不同，不能混为一谈。

## API 场景

| 方法与路径 | 场景 | 预期结果 |
| --- | --- | --- |
| `GET /health` | 服务健康检查 | HTTP 200，`status=ok` |
| `GET /api/products/1` | 正常查询商品 | HTTP 200，返回商品数据 |
| `POST /api/orders` | 有效订单 | HTTP 201，`code=ORDER_CREATED` |
| `GET /api/products/999` | 业务错误 | HTTP 200，`code=PRODUCT_NOT_FOUND` |
| `POST /api/orders` with invalid/missing fields | 参数校验失败 | HTTP 400，返回字段错误 |
| `GET /api/delay?seconds=0.08` | 可控延迟 | 延迟指定秒数后返回 HTTP 200 |

商品不存在的场景有意使用 HTTP 200 返回业务错误码，用于验证“HTTP 传输成功”和“业务处理成功”并不是同一件事。延迟参数范围限制在 0 到 2 秒，避免测试调用意外长时间挂起。

## 配置说明

`config.example.yml` 包含最小 `TestBed`、`TestSet` 和 `base_dir`，测试用例都位于 `examples/mock_api/test_cases/`。运行脚本会把 `base_dir` 解析为示例目录绝对路径，并注入临时服务地址作为执行参数，因此不需要复制仓库中的 `configs/main.example.yml`，也不会触及个人配置文件。

每个示例用例都遵循现有测试框架约定：文件名与用例类名一致，继承 `TestRunner.core.Base.Base`，在 `defineSteps()` 中通过 `def_step()` 注册操作和断言。可以把这些用例作为编写新用例的最小参考。

## 自动化验证

```bash
python -m pytest -q tests/test_mock_api_demo.py
```

测试会检查 API 的成功、业务错误、参数错误、延迟边界，并启动临时回环服务运行整个 TestRunner 用例集。它不验证真实业务系统或 MySQL 的兼容性；这些依赖仍需在专用集成环境中测试。
