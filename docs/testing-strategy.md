# 测试策略与质量保障

本文说明 AutoTestWeb 当前如何验证框架本身、测试用例执行行为与外部服务契约。文档只描述仓库中已有的测试与 CI，不把计划中的真实业务回归写成已经覆盖。

## 1. 测试分层

| 层级 | 目标 | 当前入口 | 外部依赖 |
| --- | --- | --- | --- |
| 单元测试 | 验证单个组件的状态、输入校验、异常路径和结果统计 | `tests/test_task_state.py`、`tests/test_task_lifecycle.py`、`tests/test_test_runner_core.py`、`tests/test_database_client.py` | 通过 fake/mock 隔离 Runner、日志、数据库连接和本地配置 |
| 组件/集成测试 | 验证 Flask app factory、ConfigLoader、Mock API 与 TestRunner 之间的组合行为 | `tests/test_app_factory.py`、`tests/test_config_loader.py`、`tests/test_mock_api_demo.py` | 使用内存配置、临时 YAML 或本地 Mock API，不访问真实业务服务 |
| 真实环境回归 | 验证私有业务系统、真实账号、真实 MySQL schema、异步业务状态和生产接近数据 | **当前没有纳入默认 CI** | 需要专用、获授权的测试环境和独立测试数据 |

`tests/test_mock_api_demo.py` 不只是 Mock API 的 Flask test client 检查。它还启动一个只绑定到本机回环地址的临时 HTTP 服务，通过 `submit_test_task()` 调用真实任务服务和 `TestRunner` 运行 5 个示例用例，并验证生成的 HTML 报告。因此它能验证用例发现、步骤注册、HTTP 请求、断言、步骤/用例状态和执行汇总的串联行为；但它不是对私有业务系统的端到端回归。

## 2. 可复现的测试命令

先安装测试依赖：

```bash
python -m pip install -r requirements-dev.txt
```

运行完整测试集：

```bash
python -m pytest -q
```

按目标缩小范围：

```bash
python -m pytest -q tests/test_task_state.py tests/test_task_lifecycle.py
python -m pytest -q tests/test_test_runner_core.py
python -m pytest -q tests/test_database_client.py
python -m pytest -q tests/test_app_factory.py tests/test_config_loader.py
python -m pytest -q tests/test_mock_api_demo.py
```

运行一次可观察的 Mock API 演示：

```bash
python examples/mock_api/run_demo.py
```

检查关键文件语法与常见静态错误：

```bash
python -m py_compile TestRunner/core/TestRunner.py TestRunner/services/DataBaseClient.py app/__init__.py app/routes/base_routes.py app/routes/huixin_routes.py app/services/excute_testcases.py utils/ConfigLoader.py utils/LoggerManager.py utils/task_state.py
python -m compileall -q examples/mock_api
ruff check TestRunner/core/TestRunner.py TestRunner/services/DataBaseClient.py app/services/excute_testcases.py app/routes/huixin_routes.py utils/task_state.py examples/mock_api tests --select E4,E7,E9,F --ignore F401
```

## 3. 用例选择与场景覆盖

围绕组件契约选择用例，而不是只测试理想路径。每个有状态的组件都应尽量覆盖：

- 正常路径：合法输入、预期状态和正确输出。
- 反向路径：错误输入、断言失败、外部依赖异常、无效路径或缺少必要字段。
- 边界路径：空集合、参数数量不匹配、条件缺失、重复名称、延迟上界和清理路径。
- 状态一致性：内部状态、API 返回值、统计计数与最终结果互相一致。
- 隔离性：两个 app、ConfigLoader 或 TestRunner 实例之间不能共享不应共享的状态。

当前已落地的代表性覆盖包括：

| 组件 | 已有场景 | 测试文件 |
| --- | --- | --- |
| 任务状态机/任务服务 | 合法和非法状态转换、成功/失败/异常终态、任务时间戳、配置隔离、结果快照、过期任务清理 | `test_task_state.py`、`test_task_lifecycle.py` |
| TestRunner | 成功、断言失败、步骤异常、setup/teardown 失败、空用例集、路径/导入/类名错误、同名模块隔离和资源清理 | `test_test_runner_core.py` |
| 数据库客户端 | SQL 参数绑定/条件校验、提交/回滚、游标关闭、断开后重连、拒绝嵌套事务 | `test_database_client.py` |
| Flask 配置 | 无需本地 YAML 创建 app、应用实例配置隔离、多个 ConfigLoader 路径和保存隔离 | `test_app_factory.py`、`test_config_loader.py` |
| Mock API | 成功请求、业务错误码、参数校验失败、可控延迟、全套 TestRunner 示例 | `test_mock_api_demo.py` |

## 4. 测试数据与依赖隔离

- **默认不连真实系统。** 单元测试使用 fake/mock 替代 HTTP、数据库连接和框架级依赖；测试不应读取个人的 `configs/main.yml`、真实 Cookie 或生产数据。
- **使用安全测试配置。** app factory 测试通过内存 `project_config` 或临时 YAML 创建配置，不要假定开发者的本地配置存在。
- **数据库连接用 fake 进行单元验证。** 数据库客户端单元测试验证客户端自身的调用契约，但不能证明目标 MySQL 版本、DDL、schema、事务隔离级别或权限设置完全兼容。
- **临时写入应可清理。** 使用专用测试标识；多条相关写操作放入显式事务。若业务流程必须提交后才能观察异步结果，应为已提交的数据安排明确且可重试的补偿/清理步骤。
- **不要依赖测试执行顺序。** 每个测试准备自己的输入、Mock 和临时文件；不可将前一个测试留下的状态作为后一个测试的隐式前提。
- **限制网络和等待。** Mock API 只绑定回环接口；请求使用明确 timeout，延迟验证采用小且有界的秒数。

数据库事务、参数化查询和资源管理约定详见 [数据库客户端说明](database-client.md)。用例结构与当前生命周期限制详见 [测试用例指南](test-case-guide.md)。

## 5. 断言、失败分类与结果定位

断言应同时验证协议结果和业务语义。例如，对有效订单检查 HTTP 201、业务码 `ORDER_CREATED` 和返回字段；对不存在的商品检查业务码 `PRODUCT_NOT_FOUND`，而不把 HTTP 200 错当作业务成功。

现有 TestRunner 将失败大致分为：

- **失败（`失败`）**：测试断言不成立，或所有用例执行后测试套不满足全通过条件。
- **错误（`错误`）**：发生非断言异常，例如步骤执行异常、用例模块加载错误或初始化异常。
- **跳过（`跳过`）**：某一步骤失败后，后续步骤被标记为跳过。
- **通过（`通过`）**：用例步骤按预期执行并通过断言。

问题定位顺序建议为：先看任务/测试套状态和错误摘要，再定位失败用例，最后检查步骤级状态、错误文本和请求/响应断言。完整项目任务的任务状态是 `pending/running/completed/failed/error`；它与 TestRunner 用例内部使用的中文状态枚举不同，不要将两套状态名称混为一谈。

**当前已知生命周期限制：** 核心步骤发生断言失败/异常时，现有执行路径不会自动执行该用例的 `tearDown()`。因此不应把关键数据库连接关闭或持久测试数据删除完全寄托在 `tearDown()` 上。该行为仍需要独立的执行器修复和失败路径回归覆盖。

## 6. CI 质量门禁与边界

仓库工作流 `.github/workflows/task-lifecycle-tests.yml` 在推送和面向 `main` 的 Pull Request 上执行，矩阵包括 Python 3.10、3.11 和 3.12。每个矩阵 job 会：

1. 安装 `requirements-dev.txt`。
2. 对关键运行模块执行 `py_compile`。
3. 编译 Mock API 示例目录。
4. 使用 Ruff 的 `E4/E7/E9/F` 规则检查所列关键模块、Mock API 和测试目录（当前配置忽略 `F401`）。
5. 执行完整 `pytest` 测试集。
6. 直接执行一次 `python examples/mock_api/run_demo.py --report-path reports/mock-api-demo-report.html`，核验任务终态、完整用例/步骤输出和报告生成。
7. 将该 Python 版本生成的 `reports/mock-api-demo-report.html` 上传为 CI artifact，保留 14 天供下载检查。

当前 CI 没有启动真实 MySQL，也不会向私有业务系统发出请求。因此，CI 通过代表隔离测试和静态检查通过，不代表已经完成真实业务环境验收。凡涉及 schema 兼容、登录态、异步算法、跨服务状态、权限和测试数据恢复的变更，仍应在专用且获授权的集成环境中验证，并记录环境和实际结果。

## 7. 新增测试的验收清单

新增或修改组件时，至少确认：

- [ ] 测试覆盖正常、失败或异常，以及与风险相称的边界场景。
- [ ] 对外部 HTTP/DB/登录依赖做隔离，或明确说明为什么需要真实集成环境。
- [ ] 测试检查最终状态和关键输出，而不只检查函数没有抛异常。
- [ ] 有持久副作用时，验证事务回滚、连接释放或清理策略。
- [ ] 可在新环境按文档命令重现，不依赖个人配置文件。
- [ ] Python 版本矩阵、Ruff、编译检查和全量 pytest 均通过。
- [ ] 对 CI 没覆盖的真实环境验证，在 PR 中明确标注，而不是声称已通过。
