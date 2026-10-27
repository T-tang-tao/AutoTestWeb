"""Contract and end-to-end tests for the self-contained Mock API demo."""

from examples.mock_api.server import create_app
from examples.mock_api.run_demo import run_demo


def test_mock_api_success_business_error_validation_and_delay_contracts():
    client = create_app().test_client()

    health = client.get("/health")
    assert health.status_code == 200
    assert health.get_json()["service"] == "autotestweb-mock-api"

    success = client.get("/api/products/1")
    assert success.status_code == 200
    assert success.get_json()["data"]["name"] == "Demo Product"

    business_error = client.get("/api/products/999")
    assert business_error.status_code == 200
    assert business_error.get_json()["code"] == "PRODUCT_NOT_FOUND"

    validation_error = client.post("/api/orders", json={"quantity": 0})
    assert validation_error.status_code == 400
    assert validation_error.get_json()["code"] == "VALIDATION_ERROR"

    order_success = client.post(
        "/api/orders",
        json={"product_id": 1, "quantity": 2},
    )
    assert order_success.status_code == 201
    assert order_success.get_json()["code"] == "ORDER_CREATED"

    delayed = client.get("/api/delay?seconds=0.02")
    assert delayed.status_code == 200
    assert delayed.get_json()["actual_delay"] >= 0.02

    invalid_delay = client.get("/api/delay?seconds=3")
    assert invalid_delay.status_code == 400
    assert invalid_delay.get_json()["code"] == "VALIDATION_ERROR"


def test_real_test_runner_executes_all_mock_api_cases_without_local_configs(tmp_path):
    report_path = tmp_path / "mock-api-demo-report.html"
    summary = run_demo(report_path=str(report_path))

    assert summary["status"] == "通过"
    assert summary["task_status"] == "completed"
    assert summary["duration"] >= 0
    assert summary["error"] is None
    assert summary["stats"] == {
        "total": 5,
        "passed": 5,
        "failed": 0,
        "error": 0,
        "skipped": 0,
    }
    assert summary["report_path"] == str(report_path)
    assert report_path.exists()
    report_html = report_path.read_text(encoding="utf-8")
    assert "测试执行报告" in report_html
    assert "通过：5" in report_html
    assert "Mock API：查询商品成功" in report_html
    assert "Mock API：可控延迟响应" in report_html
    assert len(summary["test_cases"]) == 5
    assert all(case["status"] == "通过" for case in summary["test_cases"])
    assert all(
        step["status"] == "通过"
        for case in summary["test_cases"]
        for step in case["steps"]
    )
