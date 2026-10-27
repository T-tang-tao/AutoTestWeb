"""Isolated tests for the reusable HTTP client wrapper."""

from types import SimpleNamespace

import pytest

import TestRunner.services.HttpClient as http_module


class FakeLogger:
    def __init__(self):
        self.debug_messages = []
        self.error_messages = []

    def debug(self, message, *args, **kwargs):
        self.debug_messages.append((message, args))

    def error(self, message, *args, **kwargs):
        self.error_messages.append((message, args))


class FakeResponse:
    def __init__(self, status_code=200, content=b'{"ok": true}', text="response text", error=None):
        self.status_code = status_code
        self.content = content
        self.text = text
        self.error = error

    def raise_for_status(self):
        if self.error:
            raise self.error


class FakeSession:
    def __init__(self, get_response=None, post_response=None, get_error=None, post_error=None):
        self.get_response = get_response or FakeResponse()
        self.post_response = post_response or FakeResponse(status_code=201)
        self.get_error = get_error
        self.post_error = post_error
        self.get_calls = []
        self.post_calls = []
        self.close_count = 0

    def get(self, url, **kwargs):
        self.get_calls.append({"url": url, **kwargs, "headers": dict(kwargs["headers"])})
        if self.get_error:
            raise self.get_error
        return self.get_response

    def post(self, url, **kwargs):
        self.post_calls.append({"url": url, **kwargs, "headers": dict(kwargs["headers"])})
        if self.post_error:
            raise self.post_error
        return self.post_response

    def close(self):
        self.close_count += 1


@pytest.fixture
def http_client_factory(monkeypatch):
    sessions = []
    logger = FakeLogger()

    def create_session():
        session = FakeSession()
        sessions.append(session)
        return session

    monkeypatch.setattr(http_module.requests, "Session", create_session)
    monkeypatch.setattr(
        http_module,
        "LoggerManager",
        lambda: SimpleNamespace(get_logger=lambda: logger),
    )
    return lambda **kwargs: (http_module.HttpClient(**kwargs), sessions, logger)


def test_get_uses_default_timeout_and_records_request_and_response(http_client_factory):
    client, sessions, _ = http_client_factory()
    response = FakeResponse(content=b'{"items": 2}')
    sessions[0].get_response = response

    result = client.get("https://service.test/items", params={"page": 2})

    call = sessions[0].get_calls[0]
    assert result is response
    assert call["url"] == "https://service.test/items"
    assert call["params"] == {"page": 2}
    assert call["timeout"] == 10
    assert call["headers"]["Accept"] == "application/json, text/plain, */*"
    assert client.last_request["method"] == "GET"
    assert client.last_request["params"] == {"page": 2}
    assert client.last_response == {"status_code": 200, "json": b'{"items": 2}'}


def test_get_merges_custom_headers_and_allows_timeout_override(http_client_factory):
    client, sessions, _ = http_client_factory()

    client.set_global_headers({"X-Client": "autotest"})
    client.get(
        "https://service.test/items",
        headers={"Accept": "application/custom", "X-Request": "one"},
        timeout=2,
    )

    call = sessions[0].get_calls[0]
    assert call["timeout"] == 2
    assert call["headers"]["Accept"] == "application/custom"
    assert call["headers"]["X-Client"] == "autotest"
    assert call["headers"]["X-Request"] == "one"


def test_post_uses_form_or_json_content_type_and_records_payload(http_client_factory):
    client, sessions, _ = http_client_factory()
    session = sessions[0]

    form_response = FakeResponse(status_code=200, content=b"form accepted")
    session.post_response = form_response
    assert client.post("https://service.test/form", data={"name": "Alice"}) is form_response

    json_response = FakeResponse(status_code=201, content=b"json accepted")
    session.post_response = json_response
    assert client.post("https://service.test/items", json={"name": "Alice"}) is json_response

    form_call, json_call = session.post_calls
    assert form_call["timeout"] == 10
    assert form_call["headers"]["Content-Type"] == "application/x-www-form-urlencoded; charset=UTF-8"
    assert form_call["data"] == {"name": "Alice"}
    assert json_call["headers"]["Content-Type"] == "application/json; charset=UTF-8"
    assert json_call["json"] == {"name": "Alice"}
    assert client.last_request["method"] == "POST"
    assert client.last_request["json"] == {"name": "Alice"}
    assert client.last_response == {"status_code": 201, "json": b"json accepted"}


@pytest.mark.parametrize("error_source", ["request", "http_status"])
def test_get_errors_follow_existing_assertion_error_path(http_client_factory, error_source):
    if error_source == "request":
        session = FakeSession(get_error=RuntimeError("connection timed out"))
    else:
        session = FakeSession(
            get_response=FakeResponse(error=RuntimeError("HTTP 503"))
        )
    client, sessions, logger = http_client_factory()
    sessions[0].get_error = session.get_error
    sessions[0].get_response = session.get_response

    with pytest.raises(AssertionError, match="request failed - error msg"):
        client.get("https://service.test/items")

    assert logger.error_messages
    assert client.last_response is None


def test_reset_closes_old_session_and_clears_recorded_state(http_client_factory):
    client, sessions, _ = http_client_factory()
    old_session = sessions[0]
    client.get("https://service.test/items")
    assert client.last_request is not None
    assert client.last_response is not None

    client.reset()

    assert old_session.close_count == 1
    assert len(sessions) == 2
    assert client.session is sessions[1]
    assert client.last_request is None
    assert client.last_response is None
