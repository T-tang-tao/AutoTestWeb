# AutoTestWeb

AutoTestWeb 是一个以 Flask 为服务层、以 Python 为执行层的自动化测试工作台。它提供测试用例发现、测试集执行、任务状态查询、HTML 报告生成，以及面向监狱评估业务的多角色接口与流程测试能力。

## 主要能力

- 从 `Business/<Module>/TestCases` 自动发现测试用例。
- 支持 YAML 测试集、顺序执行、依赖和超时配置。
- 提供 Flask API 查询配置、启动任务和读取执行状态。
- 封装 HTTP 客户端、数据库客户端和接口重试机制。
- 生成 HTML 测试报告。
- 通过测试数据工厂组织复杂表单、审批和流程数据。

## 目录结构

```text
AutoTestWeb/
├─ app/                 Flask API、路由和服务
├─ Business/            业务测试模块与测试用例
├─ TestRunner/          用例执行器、报告和基础服务
├─ utils/               配置、日志和通用工具
├─ configs/             本地配置与可提交的示例配置
├─ server.py            Web API 入口
└─ requirements.txt     Python 依赖
```

## 快速开始

建议使用 Python 3.10 或更高版本。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

Copy-Item configs/main.example.yml configs/main.yml
Copy-Item configs/TestBed.example.yml configs/TestBed.yml
Copy-Item configs/TestSet.example.yml configs/TestSet.yml

python server.py
```

API 默认监听 `http://127.0.0.1:5000`。

直接执行测试集：

```powershell
python -m TestRunner.runner
```

## 配置

`configs/main.yml` 是主配置入口，它引用测试环境和测试集配置：

```yaml
TestBedPath: ./TestBed.yml
TestSetPath: ./TestSet.yml
base_dir: ../Business
```

相对路径以 `main.yml` 所在目录为基准。真实配置已加入 `.gitignore`，请只在本地维护。

`configs/TestBed.yml` 包含 HuiXin、Ficus 和数据库连接信息。提交或分享项目时，请使用环境专用的私密配置，不要把真实地址、账号、密码、Cookie 或业务标识写入模板。

部分独立调试入口从环境变量读取账号：

```powershell
$env:HUIXIN_USERNAME = "your-user"
$env:HUIXIN_PASSWORD = "your-password"
```

## 新增测试用例

1. 在 `Business/<Module>/TestCases` 下新增 Python 用例。
2. 在用例中提供 `case_name`，或直接使用文件名作为展示名称。
3. 在 `configs/TestSet.yml` 中加入用例路径及执行参数。
4. 通过 `python -m TestRunner.runner` 或 Flask API 执行。

## 安全约定

- `logs/`、`TestRunner/logs/`、`reports/` 和本地数据库导出文件不会进入 Git。
- `configs/main*.yml`、`configs/TestBed*.yml` 和 `configs/TestSet*.yml` 仅在本地使用。
- 代码中的测试身份、环境实例 ID、表单 ID 等应通过配置或调用参数传入。
- 提交前应检查暂存区，避免真实账号、Cookie、身份证号、手机号和内网地址泄露。
