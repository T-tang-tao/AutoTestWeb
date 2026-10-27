"""MySQL client with explicit transaction boundaries and validated helper SQL.

Values are always passed separately through PyMySQL parameters. The convenience
methods only allow a deliberately small subset of SQL conditions; callers who
need a different expression should use a trusted, static SQL statement with
execute_query/execute_update and must not interpolate untrusted input.
"""

import re
from contextlib import contextmanager
from threading import RLock
from typing import Any, Dict, List, Optional, Tuple

import pymysql

from utils.LoggerManager import LoggerManager


_IDENTIFIER = r"[A-Za-z_][A-Za-z0-9_$]*"
_QUALIFIED_IDENTIFIER = rf"{_IDENTIFIER}(?:\.{_IDENTIFIER})*"
_IDENTIFIER_RE = re.compile(rf"^{_QUALIFIED_IDENTIFIER}$")
_COLUMN_RE = re.compile(
    rf"^(?P<identifier>{_QUALIFIED_IDENTIFIER})(?:\s+(?:AS\s+)?(?P<alias>{_IDENTIFIER}))?$",
    re.IGNORECASE,
)
_ORDER_ITEM_RE = re.compile(
    rf"^(?P<identifier>{_QUALIFIED_IDENTIFIER})(?:\s+(?P<direction>ASC|DESC))?$",
    re.IGNORECASE,
)


class _ConditionParser:
    """Parser for identifier comparisons joined by AND/OR, with safe placeholders."""

    _TOKEN_RE = re.compile(
        r"\s*(?:(?P<named_placeholder>%\([A-Za-z_][A-Za-z0-9_]*\)s)"
        r"|(?P<placeholder>%s)"
        r"|(?P<keyword>AND|OR|IS|NOT|NULL|LIKE|IN)\b"
        r"|(?P<identifier>[A-Za-z_][A-Za-z0-9_$]*(?:\.[A-Za-z_][A-Za-z0-9_$]*)*)"
        r"|(?P<operator><=|>=|<>|!=|=|<|>)"
        r"|(?P<lparen>\()"
        r"|(?P<rparen>\))"
        r"|(?P<comma>,))",
        re.IGNORECASE,
    )

    def __init__(self, condition: str):
        self.condition = condition
        self.tokens = self._tokenize(condition)
        self.position = 0

    @classmethod
    def _tokenize(cls, condition: str) -> List[Tuple[str, str]]:
        tokens = []
        position = 0
        while position < len(condition):
            if not condition[position:].strip():
                break
            match = cls._TOKEN_RE.match(condition, position)
            if match is None:
                raise ValueError(
                    f"不支持的 SQL 条件片段: {condition[position:]!r}"
                )
            token_kind = next(
                kind for kind, value in match.groupdict().items()
                if value is not None
            )
            token_value = match.group(token_kind)
            if token_kind == "keyword":
                token_value = token_value.upper()
            tokens.append((token_kind, token_value))
            position = match.end()
        if not tokens:
            raise ValueError("SQL 条件不能为空")
        return tokens

    def parse(self) -> List[Tuple[str, str]]:
        self._parse_expression()
        if self.position != len(self.tokens):
            raise ValueError(
                f"SQL 条件存在多余片段: {self.tokens[self.position][1]!r}"
            )
        return self.tokens

    def _current(self):
        if self.position >= len(self.tokens):
            return None, None
        return self.tokens[self.position]

    def _accept(self, kind: str, value: Optional[str] = None) -> bool:
        current_kind, current_value = self._current()
        if current_kind != kind:
            return False
        if value is not None and current_value.upper() != value.upper():
            return False
        self.position += 1
        return True

    def _expect(self, kind: str, value: Optional[str] = None) -> str:
        current_kind, current_value = self._current()
        if current_kind != kind or (
            value is not None and current_value.upper() != value.upper()
        ):
            expected = value or kind
            actual = current_value if current_value is not None else "条件结束"
            raise ValueError(f"SQL 条件格式错误：需要 {expected}，实际为 {actual!r}")
        self.position += 1
        return current_value

    def _accept_keyword(self, value: str) -> bool:
        return self._accept("keyword", value)

    def _parse_expression(self) -> None:
        self._parse_and_expression()
        while self._accept_keyword("OR"):
            self._parse_and_expression()

    def _parse_and_expression(self) -> None:
        self._parse_atom()
        while self._accept_keyword("AND"):
            self._parse_atom()

    def _parse_atom(self) -> None:
        if self._accept("lparen"):
            self._parse_expression()
            self._expect("rparen")
            return

        self._expect("identifier")
        if self._accept("operator"):
            self._expect_placeholder()
            return
        if self._accept_keyword("LIKE"):
            self._expect_placeholder()
            return
        if self._accept_keyword("NOT"):
            if self._accept_keyword("LIKE"):
                self._expect_placeholder()
                return
            if self._accept_keyword("IN"):
                self._parse_in_list()
                return
            raise ValueError("SQL 条件中的 NOT 仅支持 NOT LIKE 或 NOT IN")
        if self._accept_keyword("IS"):
            self._accept_keyword("NOT")
            self._expect("keyword", "NULL")
            return
        if self._accept_keyword("IN"):
            self._parse_in_list()
            return
        raise ValueError(
            "SQL 条件仅支持比较运算符、LIKE、IN、IS NULL 以及 AND/OR 组合"
        )

    def _expect_placeholder(self) -> None:
        if not (self._accept("placeholder") or self._accept("named_placeholder")):
            raise ValueError("SQL 条件的值必须使用 %s 或 %(name)s 参数占位符")

    def _parse_in_list(self) -> None:
        self._expect("lparen")
        self._expect_placeholder()
        while self._accept("comma"):
            self._expect_placeholder()
        self._expect("rparen")


class DataBaseClient:
    """MySQL client with explicit transaction and cursor lifecycle management."""

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        port: int = 3306,
    ):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.logger = LoggerManager().get_logger()
        self._lock = RLock()
        self._transaction_depth = 0
        self.connection = None
        self.connect()

    def connect(self):
        """Open and store a connection, reusing an existing live connection."""
        with self._lock:
            if self.connection is not None and getattr(self.connection, "open", True):
                return self.connection
            try:
                self.connection = pymysql.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    port=self.port,
                )
                self.logger.debug("Database connected successfully...")
                return self.connection
            except pymysql.MySQLError as exc:
                self.logger.error("Error connecting to MySQL: %s", exc)
                raise

    def _ensure_connection(self) -> None:
        if self.connection is None or not getattr(self.connection, "open", True):
            if self._transaction_depth:
                raise RuntimeError("事务执行期间数据库连接已关闭")
            self.connect()

    def disconnect(self) -> None:
        """Close the owned connection; a later operation can reconnect lazily."""
        with self._lock:
            if self._transaction_depth:
                raise RuntimeError("不能在事务执行期间关闭数据库连接")
            connection = self.connection
            try:
                if connection is not None and getattr(connection, "open", True):
                    connection.close()
                    self.logger.debug("Database connection closed.")
            finally:
                self.connection = None

    @contextmanager
    def get_cursor(self):
        """Yield a cursor and always close it, serializing use of this connection."""
        with self._lock:
            self._ensure_connection()
            cursor = self.connection.cursor()
            try:
                yield cursor
            finally:
                cursor.close()

    @staticmethod
    def _quote_identifier(identifier: str, label: str = "标识符") -> str:
        """Validate an identifier and quote each MySQL identifier segment."""
        if not isinstance(identifier, str) or not _IDENTIFIER_RE.fullmatch(identifier):
            raise ValueError(f"非法{label}: {identifier!r}")
        return ".".join(f"`{segment}`" for segment in identifier.split("."))

    def _format_column(self, column: str) -> str:
        if not isinstance(column, str):
            raise ValueError(f"非法字段名: {column!r}")
        column = column.strip()
        if column == "*":
            return "*"
        if column.endswith(".*"):
            table_part = column[:-2]
            return f"{self._quote_identifier(table_part, '字段名')}.*"

        match = _COLUMN_RE.fullmatch(column)
        if match is None:
            raise ValueError(f"不支持的 SELECT 字段表达式: {column!r}")
        rendered = self._quote_identifier(match.group("identifier"), "字段名")
        alias = match.group("alias")
        if alias:
            rendered += f" AS {self._quote_identifier(alias, '字段别名')}"
        return rendered

    def _format_order_by(self, order_by: str) -> str:
        pieces = [piece.strip() for piece in order_by.split(",")]
        if not pieces or any(not piece for piece in pieces):
            raise ValueError(f"非法排序字段: {order_by!r}")

        result = []
        for piece in pieces:
            match = _ORDER_ITEM_RE.fullmatch(piece)
            if match is None:
                raise ValueError(f"不支持的排序表达式: {piece!r}")
            item = self._quote_identifier(match.group("identifier"), "排序字段")
            direction = match.group("direction")
            if direction:
                item += f" {direction.upper()}"
            result.append(item)
        return ", ".join(result)

    def _prepare_condition(
        self,
        condition: Optional[str],
        params: Optional[Any],
        *,
        required: bool = False,
    ):
        if condition is None or not isinstance(condition, str) or not condition.strip():
            if required:
                raise ValueError("必须提供 WHERE 条件，避免意外操作整张表")
            if params is not None and params not in ((), [], {}):
                raise ValueError("没有 WHERE 条件时不能传入条件参数")
            return None, None

        tokens = _ConditionParser(condition).parse()
        positional_count = sum(kind == "placeholder" for kind, _ in tokens)
        named_keys = [
            value[2:-2] for kind, value in tokens if kind == "named_placeholder"
        ]
        if positional_count and named_keys:
            raise ValueError("同一 WHERE 条件不能混用位置参数和命名参数")

        if named_keys:
            if not isinstance(params, dict):
                raise ValueError("使用命名占位符时，条件参数必须是字典")
            missing = sorted(set(named_keys) - params.keys())
            if missing:
                raise ValueError(f"WHERE 条件缺少命名参数: {', '.join(missing)}")
            normalized_params = params
        else:
            if params is None:
                normalized_params = ()
            elif isinstance(params, dict):
                # Preserve the existing helper API's insertion-order mapping behavior.
                normalized_params = tuple(params.values())
            elif isinstance(params, (list, tuple)):
                normalized_params = tuple(params)
            else:
                normalized_params = (params,)
            if len(normalized_params) != positional_count:
                raise ValueError(
                    f"WHERE 条件需要 {positional_count} 个参数，"
                    f"实际收到 {len(normalized_params)} 个"
                )

        safe_tokens = []
        for kind, value in tokens:
            if kind == "identifier":
                safe_tokens.append(self._quote_identifier(value, "条件字段"))
            elif kind == "keyword":
                safe_tokens.append(value.upper())
            else:
                safe_tokens.append(value)
        return " ".join(safe_tokens), normalized_params

    def execute_query(
        self, sql: str, params: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """Execute a trusted query; pass user values via params, never interpolation."""
        self.logger.debug("sql:%s, params:%s", sql, params)
        with self._lock:
            try:
                with self.get_cursor() as cursor:
                    cursor.execute(sql, params)
                    return cursor.fetchall()
            except Exception:
                if self._transaction_depth == 0 and self.connection is not None:
                    self.connection.rollback()
                raise

    def execute_update(self, sql: str, params: Optional[Any] = None) -> int:
        """Execute trusted SQL; commit standalone updates, defer commits in a transaction."""
        self.logger.debug("sql:%s, params:%s", sql, params)
        with self._lock:
            try:
                with self.get_cursor() as cursor:
                    cursor.execute(sql, params)
                    rowcount = cursor.rowcount
                if self._transaction_depth == 0:
                    self.connection.commit()
                return rowcount
            except Exception:
                if self._transaction_depth == 0 and self.connection is not None:
                    self.connection.rollback()
                raise

    @contextmanager
    def transaction(self):
        """Commit the whole block on success; roll back and re-raise on any error.

        Nested transactions are intentionally not supported because this client does
        not implement savepoints. Callers should create one transaction per unit of
        work and keep all related updates inside that block.
        """
        with self._lock:
            self._ensure_connection()
            if self._transaction_depth:
                raise RuntimeError("不支持嵌套事务，请将操作放入同一事务上下文")
            self._transaction_depth = 1
            try:
                self.connection.begin()
                yield
                self.connection.commit()
                self.logger.debug("Transaction committed.")
            except Exception as exc:
                try:
                    if self.connection is not None:
                        self.connection.rollback()
                except Exception:
                    self.logger.exception("Transaction rollback failed.")
                self.logger.error("Transaction rolled back due to error: %s", exc)
                raise
            finally:
                self._transaction_depth = 0

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert a row; table/column names are validated and values are parameterized."""
        if not isinstance(data, dict) or not data:
            raise ValueError("insert 的 data 必须是非空字典")
        table_sql = self._quote_identifier(table, "表名")
        columns = [self._quote_identifier(key, "字段名") for key in data]
        column_sql = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO {table_sql} ({column_sql}) VALUES ({placeholders})"
        return self.execute_update(sql, tuple(data.values()))

    def update(
        self,
        table: str,
        data: Dict[str, Any],
        condition: str,
        condition_params: Optional[Any] = None,
    ) -> int:
        """Update rows only with a validated WHERE condition and parameterized values."""
        if not isinstance(data, dict) or not data:
            raise ValueError("update 的 data 必须是非空字典")
        table_sql = self._quote_identifier(table, "表名")
        condition_sql, bound_condition_params = self._prepare_condition(
            condition, condition_params, required=True
        )
        set_clause = ", ".join(
            f"{self._quote_identifier(key, '字段名')} = %s" for key in data
        )
        sql = f"UPDATE {table_sql} SET {set_clause} WHERE {condition_sql}"
        params = tuple(data.values()) + tuple(bound_condition_params or ())
        return self.execute_update(sql, params)

    def delete(
        self,
        table: str,
        condition: str,
        condition_params: Optional[Any] = None,
    ) -> int:
        """Delete rows only with a validated WHERE condition and parameterized values."""
        table_sql = self._quote_identifier(table, "表名")
        condition_sql, params = self._prepare_condition(
            condition, condition_params, required=True
        )
        sql = f"DELETE FROM {table_sql} WHERE {condition_sql}"
        return self.execute_update(sql, params)

    def select(
        self,
        table: str,
        columns: Optional[List[str]] = None,
        condition: Optional[str] = None,
        condition_params: Optional[Any] = None,
        order_by: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Select using validated identifiers/conditions and parameterized values."""
        table_sql = self._quote_identifier(table, "表名")
        if columns is None or columns == []:
            columns_sql = "*"
        else:
            if isinstance(columns, str):
                raise ValueError("columns 必须是字段名列表，而不是字符串")
            columns_sql = ", ".join(self._format_column(column) for column in columns)

        condition_sql, params = self._prepare_condition(
            condition, condition_params, required=False
        )
        sql = f"SELECT {columns_sql} FROM {table_sql}"
        if condition_sql:
            sql += f" WHERE {condition_sql}"
        if order_by:
            sql += f" ORDER BY {self._format_order_by(order_by)}"
        return self.execute_query(sql, params)
