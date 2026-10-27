"""Unit tests for database connection, transaction and SQL helper guarantees."""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import pytest


ROOT = Path(__file__).resolve().parents[1]


class FakeLogger:
    def debug(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def exception(self, *args, **kwargs):
        pass


class FakeCursor:
    def __init__(self, connection):
        self.connection = connection
        self.rowcount = 2
        self.closed = False
        self.sql = None
        self.params = None

    def execute(self, sql, params=None):
        self.sql = sql
        self.params = params
        self.connection.executed.append((sql, params))
        if self.connection.fail_execute:
            raise RuntimeError("simulated SQL failure")

    def fetchall(self):
        return [{"id": 1}]

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self):
        self.open = True
        self.begins = 0
        self.commits = 0
        self.rollbacks = 0
        self.closed = False
        self.fail_execute = False
        self.executed = []
        self.cursors = []

    def cursor(self):
        cursor = FakeCursor(self)
        self.cursors.append(cursor)
        return cursor

    def begin(self):
        self.begins += 1

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True
        self.open = False


@pytest.fixture
def db_client(monkeypatch):
    logger_module = ModuleType("utils.LoggerManager")
    logger_module.LoggerManager = type(
        "FakeLoggerManager",
        (),
        {"get_logger": lambda self: FakeLogger()},
    )
    monkeypatch.setitem(sys.modules, "utils.LoggerManager", logger_module)

    module_name = "_autotestweb_database_client_test"
    spec = importlib.util.spec_from_file_location(
        module_name, ROOT / "TestRunner" / "services" / "DataBaseClient.py"
    )
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, module_name, module)
    spec.loader.exec_module(module)

    first_connection = FakeConnection()
    connect = Mock(return_value=first_connection)
    monkeypatch.setattr(module.pymysql, "connect", connect)

    client = module.DataBaseClient(
        host="localhost",
        user="test_user",
        password="not-a-real-password",
        database="test_db",
    )
    yield client, first_connection, connect, module
    if client.connection is not None:
        client.disconnect()


def test_insert_validates_identifiers_parameterizes_values_and_closes_cursor(db_client):
    client, connection, _, _ = db_client

    affected = client.insert("users", {"name": "Alice; DROP TABLE users"})

    assert affected == 2
    sql, params = connection.executed[0]
    assert sql == "INSERT INTO `users` (`name`) VALUES (%s)"
    assert params == ("Alice; DROP TABLE users",)
    assert connection.commits == 1
    assert connection.cursors[0].closed


def test_transaction_commits_once_after_multiple_updates(db_client):
    client, connection, _, _ = db_client

    with client.transaction():
        client.insert("users", {"name": "Alice"})
        client.update("users", {"name": "Bob"}, "id = %s", (7,))
        assert connection.commits == 0
        assert connection.rollbacks == 0

    assert connection.begins == 1
    assert connection.commits == 1
    assert connection.rollbacks == 0
    assert all(cursor.closed for cursor in connection.cursors)


def test_transaction_rolls_back_when_body_raises(db_client):
    client, connection, _, _ = db_client

    with pytest.raises(RuntimeError, match="business operation failed"):
        with client.transaction():
            client.update("users", {"name": "Bob"}, "id = %s", (7,))
            raise RuntimeError("business operation failed")

    assert connection.begins == 1
    assert connection.commits == 0
    assert connection.rollbacks == 1
    assert client._transaction_depth == 0
    assert all(cursor.closed for cursor in connection.cursors)


def test_standalone_update_failure_rolls_back_and_closes_cursor(db_client):
    client, connection, _, _ = db_client
    connection.fail_execute = True

    with pytest.raises(RuntimeError, match="simulated SQL failure"):
        client.execute_update("UPDATE users SET name = %s", ("Bob",))

    assert connection.commits == 0
    assert connection.rollbacks == 1
    assert connection.cursors[0].closed


def test_disconnect_then_query_reconnects_and_stores_new_connection(db_client, monkeypatch):
    client, first_connection, connect, module = db_client
    second_connection = FakeConnection()
    connect.side_effect = [first_connection, second_connection]

    client.disconnect()
    assert first_connection.closed
    assert client.connection is None

    result = client.execute_query("SELECT 1")

    assert result == [{"id": 1}]
    assert connect.call_count == 2
    assert client.connection is second_connection
    assert second_connection.cursors[0].closed


def test_select_quotes_identifiers_and_keeps_values_parameterized(db_client):
    client, connection, _, _ = db_client

    result = client.select(
        "users",
        columns=["id", "display_name"],
        condition="status = %s AND age >= %s",
        condition_params=("active", 18),
        order_by="id DESC",
    )

    assert result == [{"id": 1}]
    sql, params = connection.executed[0]
    assert sql == (
        "SELECT `id`, `display_name` FROM `users` "
        "WHERE `status` = %s AND `age` >= %s ORDER BY `id` DESC"
    )
    assert params == ("active", 18)
    assert connection.cursors[0].closed


def test_select_and_delete_support_named_parameters(db_client):
    client, connection, _, _ = db_client

    client.select(
        "users",
        condition="id = %(user_id)s",
        condition_params={"user_id": 11},
    )
    client.delete(
        "users",
        "id = %(user_id)s",
        {"user_id": 12},
    )

    assert connection.executed[0][1] == {"user_id": 11}
    assert connection.executed[1][1] == {"user_id": 12}


def test_update_combines_named_where_and_set_parameters_without_mixing_styles(db_client):
    client, connection, _, _ = db_client

    client.update(
        "users",
        {"name": "New name"},
        "id = %(user_id)s",
        {"user_id": 12},
    )

    sql, params = connection.executed[0]
    assert sql == (
        "UPDATE `users` SET `name` = %(__set_value_0)s "
        "WHERE `id` = %(user_id)s"
    )
    assert params == {"user_id": 12, "__set_value_0": "New name"}


@pytest.mark.parametrize(
    ("operation", "args"),
    [
        ("select", ("users; DROP TABLE users",)),
        ("select", ("users",)),
        ("insert", ("users; DROP TABLE users", {"name": "x"})),
        ("update", ("users", {"name": "x"}, "", None)),
        ("delete", ("users", "", None)),
    ],
)
def test_rejects_unsafe_identifiers_or_missing_where_clause(
    db_client, operation, args
):
    client, connection, _, _ = db_client

    if operation == "select" and args == ("users",):
        with pytest.raises(ValueError, match="排序表达式"):
            client.select("users", order_by="id DESC; DROP TABLE users")
    elif operation == "select":
        with pytest.raises(ValueError, match="表名"):
            client.select(*args)
    elif operation == "insert":
        with pytest.raises(ValueError, match="表名"):
            client.insert(*args)
    elif operation == "update":
        with pytest.raises(ValueError, match="WHERE"):
            client.update(*args)
    else:
        with pytest.raises(ValueError, match="WHERE"):
            client.delete(*args)

    assert connection.executed == []


@pytest.mark.parametrize(
    ("condition", "params"),
    [
        ("id = 1 OR 1=1", None),
        ("name = %s; DROP TABLE users", ("x",)),
        ("status = %s", ()),
        ("id = %(user_id)s", None),
        ("id = %s AND age = %s", (1,)),
    ],
)
def test_rejects_unsupported_conditions_and_parameter_mismatches(
    db_client, condition, params
):
    client, connection, _, _ = db_client

    with pytest.raises(ValueError):
        client.select("users", condition=condition, condition_params=params)

    assert connection.executed == []


def test_context_closes_cursor_even_when_query_raises(db_client):
    client, connection, _, _ = db_client
    connection.fail_execute = True

    with pytest.raises(RuntimeError, match="simulated SQL failure"):
        client.execute_query("SELECT * FROM users")

    assert connection.rollbacks == 1
    assert connection.cursors[0].closed


def test_nested_transactions_are_rejected_without_committing_inner_work(db_client):
    client, connection, _, _ = db_client

    with client.transaction():
        with pytest.raises(RuntimeError, match="不支持嵌套事务"):
            with client.transaction():
                pass
        client.insert("users", {"name": "one transaction"})

    assert connection.begins == 1
    assert connection.commits == 1
    assert connection.rollbacks == 0
