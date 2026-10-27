"""Tests for app factory configuration isolation."""

from copy import deepcopy

import app as app_module


def _project_config(host):
    return {
        "TestBed": {"env": "unit-test", "host": host},
        "TestSet": {"test_cases": []},
        "base_dir": "/tmp/autotestweb-unit-tests",
    }


def test_test_app_factory_does_not_load_local_yaml(monkeypatch):
    from utils import ConfigLoader as config_loader_module

    def unexpected_loader(*args, **kwargs):
        raise AssertionError("test factory must not read the local project config")

    monkeypatch.setattr(config_loader_module, "ConfigLoader", unexpected_loader)
    application = app_module.create_app(
        test_config={"TESTING": True},
        project_config=_project_config("http://test-service"),
    )

    response = application.test_client().get("/")

    assert response.status_code == 200
    assert response.get_json()["status"] == "success"


def test_multiple_apps_keep_independent_project_config():
    app_one = app_module.create_app(
        test_config={"TESTING": True},
        project_config=_project_config("http://service-one"),
    )
    app_two = app_module.create_app(
        test_config={"TESTING": True},
        project_config=_project_config("http://service-two"),
    )

    one_config = app_one.test_client().get("/huixin/getConfig").get_json()["data"]
    two_config = app_two.test_client().get("/huixin/getConfig").get_json()["data"]

    assert one_config["host"] == "http://service-one"
    assert two_config["host"] == "http://service-two"
    assert app_one.extensions["config_loader"] is not app_two.extensions["config_loader"]


def test_in_memory_config_loader_does_not_share_mutable_input():
    original = _project_config("http://original")
    application = app_module.create_app(
        test_config={"TESTING": True},
        project_config=original,
    )
    original["TestBed"]["host"] = "http://mutated-outside"
    loader = application.extensions["config_loader"]

    assert loader.config["TestBed"]["host"] == "http://original"
    returned = loader.get_config()
    returned["TestBed"]["host"] = "http://mutated-return-value"
    assert loader.config["TestBed"]["host"] == "http://original"


def test_config_save_is_scoped_to_the_app_instance():
    app_one = app_module.create_app(
        test_config={"TESTING": True},
        project_config=_project_config("http://service-one"),
    )
    app_two = app_module.create_app(
        test_config={"TESTING": True},
        project_config=_project_config("http://service-two"),
    )
    payload = {
        "HuiXin": {
            "users": {
                "criminal": {"username": "test-user"}
            }
        },
        "env": "updated-test",
    }

    result = app_one.test_client().post("/huixin/saveConfig", json=payload)

    assert result.status_code == 200
    one_config = app_one.test_client().get("/huixin/getConfig").get_json()["data"]
    two_config = app_two.test_client().get("/huixin/getConfig").get_json()["data"]
    assert one_config["env"] == "updated-test"
    assert one_config["HuiXin"]["users"]["criminal"]["id"] == "test-user"
    assert two_config["host"] == "http://service-two"


def test_factory_without_project_config_is_safe_when_testing_enabled():
    application = app_module.create_app(test_config={"TESTING": True})

    assert application.test_client().get("/").status_code == 200
    assert application.extensions["config_loader"].config["TestSet"] == {
        "test_cases": []
    }
