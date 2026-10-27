"""Contract tests for the versioned, business-agnostic API routes."""

from types import SimpleNamespace

import app.routes.api_routes as api_routes
from app import create_app


def _project_config(base_dir=None):
    return {
        "TestBed": {"service": {"base_url": "http://service.test"}},
        "TestSet": {"test_cases": []},
        "base_dir": str(base_dir) if base_dir else "/tmp/autotestweb-test-cases",
    }


def test_generic_test_bed_config_does_not_require_huixin_schema():
    app = create_app(
        test_config={"TESTING": True},
        project_config=_project_config(),
    )
    client = app.test_client()
    new_config = {"service": {"base_url": "http://another-service.test"}}

    response = client.put("/api/v1/config/test-bed", json=new_config)

    assert response.status_code == 200
    assert response.get_json()["status"] == "success"
    current = client.get("/api/v1/config/test-bed")
    assert current.status_code == 200
    assert current.get_json()["data"] == new_config


def test_generic_task_submission_uses_explicit_cases_and_returns_accepted(monkeypatch):
    app = create_app(
        test_config={"TESTING": True},
        project_config=_project_config(),
    )
    submitted = {}

    def fake_submit(config, params, report_dir=None):
        submitted["config"] = config
        submitted["params"] = params
        submitted["report_dir"] = report_dir
        return "task-123"

    class FakeTaskManager:
        def get_task(self, task_id):
            assert task_id == "task-123"
            return SimpleNamespace(status="pending")

    monkeypatch.setattr(api_routes, "submit_test_task", fake_submit)
    monkeypatch.setattr(api_routes, "TestTaskManager", FakeTaskManager)

    response = app.test_client().post(
        "/api/v1/tasks",
        json={
            "test_cases": [
                {
                    "path": "PrisonAssessmentSystem/TestCases/Assessment/InPrison/sample.py",
                    "name": "sample",
                }
            ],
            "params": {"record_id": "record-1"},
        },
    )

    assert response.status_code == 202
    assert response.get_json()["status"] == "success"
    assert response.get_json()["data"] == {
        "task_id": "task-123",
        "status": "pending",
    }
    assert submitted["config"]["TestSet"]["test_cases"] == [
        {
            "path": "PrisonAssessmentSystem/TestCases/Assessment/InPrison/sample.py",
            "name": "sample",
        }
    ]
    assert submitted["params"] == {"record_id": "record-1"}


def test_generic_task_submission_rejects_invalid_case_paths(monkeypatch):
    app = create_app(
        test_config={"TESTING": True},
        project_config=_project_config(),
    )
    monkeypatch.setattr(
        api_routes,
        "submit_test_task",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("invalid payload must not create a task")
        ),
    )

    response = app.test_client().post(
        "/api/v1/tasks",
        json={"test_cases": [{"path": "../README.md"}]},
    )

    assert response.status_code == 400
    assert response.get_json()["status"] == "error"


def test_generic_task_status_returns_versioned_report_url(monkeypatch):
    app = create_app(
        test_config={"TESTING": True},
        project_config=_project_config(),
    )
    payload = {
        "task_id": "task-123",
        "status": "completed",
        "report_available": True,
        "report_url": "/huixin/getTaskReport/task-123",
    }

    class FakeTaskManager:
        def get_task(self, task_id):
            assert task_id == "task-123"
            return SimpleNamespace(to_dict=lambda: payload)

    monkeypatch.setattr(api_routes, "TestTaskManager", FakeTaskManager)

    response = app.test_client().get("/api/v1/tasks/task-123")

    assert response.status_code == 200
    assert response.get_json()["data"]["report_url"] == (
        "/api/v1/tasks/task-123/report"
    )


def test_generic_task_report_downloads_html(monkeypatch, tmp_path):
    app = create_app(
        test_config={"TESTING": True},
        project_config=_project_config(),
    )
    report_path = tmp_path / "report.html"
    report_path.write_text("<html>report</html>", encoding="utf-8")

    class FakeTask:
        task_id = "task-123"
        status = "completed"
        report_error = None

        @staticmethod
        def get_report_path():
            return report_path

    class FakeTaskManager:
        def get_task(self, task_id):
            assert task_id == "task-123"
            return FakeTask()

    monkeypatch.setattr(api_routes, "TestTaskManager", FakeTaskManager)

    response = app.test_client().get("/api/v1/tasks/task-123/report")

    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert response.data == b"<html>report</html>"


def test_generic_test_case_list_returns_relative_paths(tmp_path):
    business_root = tmp_path / "Business"
    case_dir = business_root / "SampleSystem" / "TestCases" / "Smoke"
    case_dir.mkdir(parents=True)
    (business_root / "SampleSystem" / "__init__.py").write_text(
        'module_name = "Sample System"\n',
        encoding="utf-8",
    )
    (case_dir / "sample_case.py").write_text(
        'case_name = "Sample case"\n',
        encoding="utf-8",
    )

    app = create_app(
        test_config={"TESTING": True},
        project_config=_project_config(business_root),
    )

    response = app.test_client().get("/api/v1/test-cases")

    assert response.status_code == 200
    items = response.get_json()["data"]
    assert items[0]["label"] == "Sample System"
    assert items[0]["path"] == "SampleSystem/TestCases"
    assert items[0]["children"][0]["path"] == (
        "SampleSystem/TestCases/Smoke"
    )
    assert items[0]["children"][0]["children"][0]["path"] == (
        "SampleSystem/TestCases/Smoke/sample_case.py"
    )


def test_legacy_huixin_routes_remain_available():
    app = create_app(
        test_config={"TESTING": True},
        project_config=_project_config(),
    )
    response = app.test_client().get("/huixin/getConfig")

    assert response.status_code == 200
    assert response.get_json()["data"] == {
        "service": {"base_url": "http://service.test"}
    }


def test_legacy_huixin_task_submission_keeps_assessment_adapter(monkeypatch):
    import app.routes.huixin_routes as huixin_routes

    app = create_app(
        test_config={"TESTING": True},
        project_config=_project_config(),
    )
    selected_cases = [
        {
            "path": "PrisonAssessmentSystem/TestCases/Assessment/InPrison/sample.py",
            "name": "legacy_sample",
        }
    ]

    def fake_select(payload):
        assert payload["assessment"] == "in_base"
        return selected_cases

    def fake_submit(cases, params, status_code, message):
        assert cases == selected_cases
        assert params == {"record_id": "record-legacy"}
        return {"task_id": "legacy-task", "status": "pending"}, message, status_code

    monkeypatch.setattr(huixin_routes, "get_huixin_test_cases", fake_select)
    monkeypatch.setattr(huixin_routes, "submit_test_cases", fake_submit)

    response = app.test_client().post(
        "/huixin/executeTestCases",
        json={
            "assessment": "in_base",
            "params": {"record_id": "record-legacy"},
        },
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "success"
    assert response.get_json()["data"]["task_id"] == "legacy-task"
