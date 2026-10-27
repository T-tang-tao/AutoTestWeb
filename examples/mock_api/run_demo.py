"""Run the repository's TestRunner against a local Mock API.

With no --base-url, the demo starts an ephemeral loopback server in-process and
shuts it down after the TestRunner has produced its result summary. To use a
separately started mock server, pass --base-url http://127.0.0.1:5010.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from threading import Thread
from typing import Optional

import requests
import yaml
from werkzeug.serving import make_server


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_DIR = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from TestRunner.core.TestRunner import TestRunner  # noqa: E402
from examples.mock_api.server import create_app  # noqa: E402


CONFIG_PATH = EXAMPLE_DIR / "config.example.yml"


def _wait_for_health(base_url: str, attempts: int = 40) -> None:
    """Wait briefly for the local or separately started service to be ready."""
    last_error = None
    for _ in range(attempts):
        try:
            response = requests.get(f"{base_url.rstrip('/')}/health", timeout=0.25)
            if response.status_code == 200 and response.json().get("status") == "ok":
                return
            last_error = RuntimeError(
                f"Mock API 健康检查失败: HTTP {response.status_code}"
            )
        except requests.RequestException as exc:
            last_error = exc
        time.sleep(0.025)
    raise RuntimeError(f"Mock API 未就绪: {last_error}")


def run_demo(base_url: Optional[str] = None) -> dict:
    """Run all sample TestRunner cases and return a JSON-serializable summary."""
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    # Resolve case paths against this example folder rather than the caller's CWD.
    config["base_dir"] = str(EXAMPLE_DIR)

    mock_server = None
    server_thread = None
    runner = None

    if base_url is None:
        mock_server = make_server(
            "127.0.0.1",
            0,
            create_app(),
            threaded=True,
        )
        base_url = f"http://127.0.0.1:{mock_server.server_port}"
        server_thread = Thread(target=mock_server.serve_forever, daemon=True)
        server_thread.start()

    base_url = base_url.rstrip("/")
    try:
        _wait_for_health(base_url)
        runner = TestRunner(config=config, params={"base_url": base_url})
        runner.run()
        details = runner.get_test_instances_details()

        cases = []
        for case in details.get("test_cases", []):
            cases.append({
                "name": case.get("test_instance_name") or case.get("test_class_name"),
                "status": case.get("test_status"),
                "steps": [
                    {"name": step.get("name"), "status": step.get("status")}
                    for step in case.get("steps", [])
                ],
                "error": case.get("error"),
            })

        return {
            "base_url": base_url,
            "status": runner.test_set_status,
            "stats": dict(runner.stats),
            "test_cases": cases,
        }
    finally:
        if runner is not None:
            runner.cleanup_resources()
        if mock_server is not None:
            mock_server.shutdown()
            mock_server.server_close()
            if server_thread is not None:
                server_thread.join(timeout=2)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="运行 AutoTestWeb Mock API 示例")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("MOCK_API_BASE_URL"),
        help="连接已启动的 Mock API，例如 http://127.0.0.1:5010；省略则自动启动临时本地服务",
    )
    args = parser.parse_args(argv)

    summary = run_demo(args.base_url)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["status"] == "通过" else 1


if __name__ == "__main__":
    raise SystemExit(main())
