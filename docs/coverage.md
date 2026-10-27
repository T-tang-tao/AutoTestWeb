# 核心模块覆盖率报告

## 覆盖范围

项目通过 `pytest-cov` 采集以下仓库代码的语句和分支覆盖率：

- `TestRunner/`：用例发现、执行生命周期、步骤状态和报告生成等核心测试框架。
- `app/`：Flask 应用工厂、任务服务与 API 路由。
- `utils/`：配置、日志和任务状态相关工具。

测试代码、`examples/mock_api/` 演示服务和第三方依赖不纳入覆盖率分母。当前阶段不设定任意的最低百分比门槛；CI 生成的实际数据作为可复查的基线，后续再根据关键模块风险设计质量门禁。

## 本地运行

安装开发依赖：

```bash
python -m pip install -r requirements-dev.txt
```

运行全量测试并生成终端、XML 和 HTML 报告：

```bash
python -m pytest -q --cov=TestRunner --cov=app --cov=utils --cov-branch --cov-report=term-missing:skip-covered --cov-report=xml:coverage.xml --cov-report=html:htmlcov
```

HTML 报告入口为 `htmlcov/index.html`，XML 报告为 `coverage.xml`。生成物已在 `.gitignore` 中忽略，不应提交进版本库。

## GitHub Actions

CI 对 Python 3.10、3.11 和 3.12 分别运行同一组测试和覆盖率命令。每个 job 会上传名为 `core-coverage-python-<版本>` 的 artifact，内含 HTML 与 XML 报告，保留 14 天。进入对应 Actions run 的页面，在 Artifacts 区域下载即可检查细节。

## 如何解读

- 语句覆盖率表示测试执行到的可执行语句比例；分支覆盖率用于识别条件分支是否都被测试触达。
- 覆盖率不衡量断言是否充分，也不保证测试数据质量、业务需求覆盖或外部系统集成正确性。
- CI 默认使用 fake/mock 隔离数据库与私有业务系统；覆盖率结果不能被描述为已完成真实业务系统回归。
- 简历或项目介绍中的百分比，应以最新且可打开的 CI artifact/终端报告为准，不使用手工估算值。
