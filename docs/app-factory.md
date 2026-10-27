# Flask 应用工厂与测试配置

## 生产/本地启动

保持现有启动方式不变。准备本地配置文件后运行：

```powershell
Copy-Item configs/main.example.yml configs/main.yml
Copy-Item configs/TestBed.example.yml configs/TestBed.yml
Copy-Item configs/TestSet.example.yml configs/TestSet.yml
python server.py
```

macOS / Linux 使用 `cp` 复制示例配置。真实账号、Cookie 和数据库配置只保留在本地文件中，不应提交到 Git。

`app` 模块的导入本身不再读取主 YAML 或应用级日志配置。普通应用实例调用 `create_app()` 时才创建独立的 `ConfigLoader`，并从 `configs/main.yml` 加载项目配置；也可以通过 `create_app(config_path=...)` 指定其他主配置文件。

## 测试中创建独立应用

测试可以注入内存项目配置，不需要创建个人本地 YAML，也不会连接真实业务系统：

```python
from app import create_app

app = create_app(
    test_config={"TESTING": True},
    project_config={
        "TestBed": {"env": "unit-test", "host": "http://example.test"},
        "TestSet": {"test_cases": []},
        "base_dir": "tests/fixtures",
    },
)
client = app.test_client()
response = client.get("/huixin/getConfig")
assert response.status_code == 200
```

这里的 `test_config` 用来设置 Flask 自己的配置，例如 `TESTING`；`project_config` 则是项目使用的 TestBed、TestSet 和基础目录等配置。两者用途不同，不要把测试服务地址或业务参数误放到 Flask 的配置键中。

如果测试依赖已有的 fake/config loader，也可以传入 `config_loader`。它应提供 `config` 字典、`get_config()` 和 `save_test_bed(data)` 方法。不能同时传入 `config_loader` 与 `project_config`。

```python
app_one = create_app(
    test_config={"TESTING": True},
    project_config={"TestBed": {"env": "one"}, "TestSet": {"test_cases": []}},
)
app_two = create_app(
    test_config={"TESTING": True},
    project_config={"TestBed": {"env": "two"}, "TestSet": {"test_cases": []}},
)

assert app_one.extensions["config_loader"] is not app_two.extensions["config_loader"]
```

当只传入 `test_config={"TESTING": True}` 时，工厂使用安全的内存空配置，而不是退回去读取本地 `configs/main.yml`。测试若需要完整配置，应显式提供 `project_config` 或 fake loader。

## 配置与日志边界

- 每个 `ConfigLoader(path=...)` 都是独立实例，不会因先前创建过其他 loader 而意外复用旧路径或配置。
- 路由通过当前 Flask 实例的 `app.extensions["config_loader"]` 访问对应 loader，多个 app 的配置不会写进路由模块级全局变量。
- 普通应用实例在配置加载后应用 YAML 中的日志配置。测试实例不会使用项目本地日志路径重新配置共享 logger。
- 当前 issue 不调整 CORS 策略、启动脚本中的 debug 参数或鉴权行为；这些不属于本次应用工厂改造范围。

## 验证命令

```bash
python -m pytest -q tests/test_app_factory.py tests/test_config_loader.py
```

这些测试会验证：导入与创建测试 app 不要求个人 YAML 文件、两个 app 实例之间配置互不影响、内存配置不会因外部对象修改而变化，以及不同路径的 ConfigLoader 不共享状态。
