# AutoTestWeb

[![Task lifecycle tests](https://github.com/T-tang-tao/AutoTestWeb/actions/workflows/task-lifecycle-tests.yml/badge.svg?branch=main)](https://github.com/T-tang-tao/AutoTestWeb/actions/workflows/task-lifecycle-tests.yml)

AutoTestWeb 是一个基于 **Python + Flask** 的自动化测试工作台，用于组织 Python 测试用例、执行多步骤业务流程、跟踪任务状态，并复用 HTTP、数据库和测试数据能力。

仓库包含独立的 Mock API 示例，无需真实业务账号或 MySQL，即可复现核心的用例加载、步骤执行、断言、HTTP 调用与结果统计。

## 一分钟运行 Demo

需要 Python 3.10 或更高版本。创建虚拟环境：

```bash
python -m venv .venv
```

激活虚拟环境后安装项目和开发测试依赖：

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python examples/mock_api/run_demo.py
```

macOS / Linux：

```bash
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python examples/mock_api/run_demo.py
```

Demo 会在 `127.0.0.1` 启动临时 Mock API，运行 5 个 TestRunner 示例用例，输出 JSON 摘要并在结束后关闭服务。不读取个人的 `configs/main.yml`，不需要真实凭据或 MySQL。

成功时，执行摘要包含以下统计（命令会输出每个用例和步骤的完整结果）：

```json
{
  "status": "通过",
  "stats": {
    "total": 5,
    "passed": 5,
    "failed": 0,
    "error": 0,
    "skipped": 0
  }
}
```

GitHub Actions 也会实际运行 `python examples/mock_api/run_demo.py`。查看 [CI 运行记录](https://github.com/T-tang-tao/AutoTestWeb/actions/workflows/task-lifecycle-tests.yml) 可检查测试矩阵、Demo 命令输出和失败细节。上面的结果属于 Mock API 示例执行，不代表私有业务系统已完成回归。

## Demo 场景

| 场景 | 预期结果 |
| --- | --- |
| 查询存在的商品 | HTTP 200，返回商品字段 |
| 创建订单 | HTTP 201，返回订单信息 |
| 查询不存在的商品 | HTTP 200，业务码为 `PRODUCT_NOT_FOUND` |
| 提交无效订单 | HTTP 400，返回字段校验错误 |
| 可控延迟响应 | 等待指定秒数后返回 |

商品不存在的场景特意以 HTTP 200 返回业务错误码，用来验证“传输成功”不等于“业务成功”。

Demo 使用现有 `Base`、`defineSteps()` 和 `def_step()` 约定，并通过本地 HTTP 请求运行真实的 `TestRunner`。它能验证框架主链路，但不代替真实业务系统的集成测试。详见 [Mock API 演示指南](docs/mock-api-demo.md)。

## 连接自己的测试环境

真实业务测试依赖对应的服务地址、账号、Cookie 和数据环境。安装运行时依赖后复制配置模板：

```bash
python -m pip install -r requirements.txt
```

Windows PowerShell：

```powershell
Copy-Item configs/main.example.yml configs/main.yml
Copy-Item configs/TestBed.example.yml configs/TestBed.yml
Copy-Item configs/TestSet.example.yml configs/TestSet.yml
```

macOS / Linux：

```bash
cp configs/main.example.yml configs/main.yml
cp configs/TestBed.example.yml configs/TestBed.yml
cp configs/TestSet.example.yml configs/TestSet.yml
```

编辑本地 `TestBed.yml` 中的服务地址、账号及数据库配置后，在受控的本地或内网环境启动：

```bash
python server.py
```

默认地址为 `http://127.0.0.1:5000`。当前服务没有完整的鉴权/访问控制能力，只应在受控开发环境运行，不要直接暴露到公网。

执行本地配置的测试集：

```bash
python -m TestRunner.runner
```

## 主要 API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/` | 健康检查 |
| `GET` | `/getTestCases` | 枚举可发现的测试用例 |
| `GET` | `/huixin/getConfig` | 获取 TestBed 配置 |
| `POST` | `/huixin/saveConfig` | 保存 TestBed 配置 |
| `POST` | `/huixin/executeTestCases` | 按评估类型提交测试任务 |
| `GET` | `/huixin/getTaskStatus/<task_id>` | 查询任务状态与步骤结果 |
| `POST` | `/huixin/createReport` | 提交固定的业务报告创建用例 |

任务创建后返回 `task_id`。状态查询响应包含任务级 `status`（`pending/running/completed/failed/error`）、进度、创建/开始/结束时间、耗时、失败摘要与结果快照。TestRunner 内部用例和步骤状态使用中文枚举，与任务级状态不是同一组值。

注意：`/huixin/createReport` 提交的是一个固定的业务报告创建用例；`TestRunner/extensions/ReportGenerator.py` 是独立 HTML 报告组件，并未被任务查询 API 直接调用。目前尚无完整的 HTML 报告下载 API 契约。

## 测试与 CI

安装开发依赖后运行完整测试集：

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

只运行 Mock API 端到端演示测试：

```bash
python -m pytest -q tests/test_mock_api_demo.py
```

CI 在推送和面向 `main` 的 Pull Request 上运行，矩阵覆盖 Python 3.10、3.11 和 3.12。每个环境执行关键模块语法编译、Mock API 示例编译、Ruff 静态检查、完整 pytest 和一次真实的 Mock API Demo 命令。

## 文档导航

- [架构与执行链路](docs/architecture.md)：模块边界、时序图、设计取舍和已知限制。
- [测试策略与质量保障](docs/testing-strategy.md)：分层测试、数据隔离、失败分类与 CI 范围。
- [测试用例编写指南](docs/test-case-guide.md)：命名、步骤注册、参数传递和失败路径限制。
- [Mock API 演示指南](docs/mock-api-demo.md)：本地服务、API 场景与运行说明。
- [应用工厂与测试配置](docs/app-factory.md)：独立 Flask app 与内存配置。
- [数据库客户端说明](docs/database-client.md)：参数绑定、事务、连接生命周期与清理责任。

## 当前边界

- 任务状态保存在进程内；服务重启会丢失历史任务，多进程之间不共享状态。
- 任务通过后台线程执行，TestRunner 当前按声明顺序串行执行用例。
- `concurrent`、`timeout`、`depends_on` 尚未形成通用调度能力；任务级取消也尚未正式启用。
- 核心步骤断言失败或异常时，当前执行路径不会自动调用用例的 `tearDown()`；关键资源清理不能完全依赖该方法。
- 默认 CI 不连接真实 MySQL 或私有业务系统；真实环境回归需单独执行并记录结果。
- `ReportGenerator` 类已存在，但完整的报告保存/下载 API 尚未接通。

本仓库目前未声明开源许可证；获得明确授权前，请将代码用于查看与学习。
