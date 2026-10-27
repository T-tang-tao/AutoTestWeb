# 数据库客户端使用与事务约定

本项目的 MySQL 封装位于 `TestRunner/services/DataBaseClient.py`。本文说明该客户端当前提供的事务语义、辅助 SQL 方法的安全边界和资源释放要求。

## 连接和游标生命周期

- 创建 `DataBaseClient` 时会尝试建立一个数据库连接；连接关闭后，下一次查询/更新会尝试重新连接，并把新连接保存到客户端实例中。
- `get_cursor()` 是上下文管理器，游标在正常返回和异常情况下都会关闭。
- `disconnect()` 会关闭当前连接并将实例中的连接引用清空。下一次操作会按需重连。
- 不要在显式事务执行期间调用 `disconnect()`。如果连接管理由用例负责，应在其 `tearDown` 或外层 `finally` 中关闭连接。
- 当前 `TestRunner.cleanup_resources()` 会在结果快照完成后，尝试关闭用例实例暴露的 `db.disconnect()`，然后清理用例实例与动态导入的模块。若应用持有共享数据库客户端，不应把共享实例挂载到用例的 `db` 属性上。

## 事务语义

### 单条更新

`insert`、`update`、`delete` 以及直接调用 `execute_update` 时，如果当前不在显式事务上下文，成功后自动提交；SQL 执行失败时会尝试回滚并重新抛出异常。

```python
client.insert("users", {"name": "Alice"})
client.update("users", {"name": "Bob"}, "id = %s", (42,))
```

### 多条语句作为一个事务

在 `with client.transaction():` 中，更新语句不会各自提交。整个代码块正常结束时提交一次；任何异常都会回滚事务并将异常继续抛给调用方。

```python
try:
    with client.transaction():
        client.update("orders", {"status": "paid"}, "id = %s", (order_id,))
        client.insert("audit_log", {"order_id": order_id, "action": "paid"})
except Exception:
    # 处理或记录失败；事务中的更新已回滚
    raise
```

当前实现不支持嵌套事务，也没有 savepoint。应将属于同一业务操作的所有语句放在一个事务块中，不要在内部再打开第二个 `transaction()`。事务上下文会持有该客户端的锁，因此应避免在事务内执行慢网络请求或长时间等待。

测试临时写入可以使用 `rollback_on_success=True`，即使代码块正常退出也会回滚：

```python
with client.transaction(rollback_on_success=True):
    client.insert("temporary_users", {"name": "test-user"})
    # 在事务内执行断言或查询；结束时写入会回滚
```

只应对专用测试数据库中的事务型表使用此模式。MySQL 回滚不能撤销非事务型表的写入、HTTP 请求或其他外部副作用。另需注意：如果事务中的数据库操作报错，即使调用方在块内捕获原始异常，事务仍会被标记为失败；退出时会回滚并抛出 `RuntimeError`，防止部分写入意外提交。

### 查询

`select` 和 `execute_query` 不会提交事务。若执行查询本身异常且当前不在显式事务中，客户端会尝试回滚并继续抛出异常。显式事务中的错误由外层事务统一回滚。

## SQL 辅助方法的安全边界

值必须使用独立参数，不要把用户输入拼接到 SQL 字符串中。

```python
rows = client.select(
    "users",
    columns=["id", "display_name"],
    condition="status = %s AND age >= %s",
    condition_params=("active", 18),
    order_by="id DESC",
)
```

辅助方法 `insert`、`update`、`delete`、`select` 会校验表名、字段名、别名和排序字段，并用反引号引用合法标识符。辅助 `condition` 仅接受受限的条件表达式：字段比较、`LIKE`/`NOT LIKE`、`IN`/`NOT IN`、`IS [NOT] NULL`，以及通过括号和 `AND`/`OR` 组合的表达式。值只能通过 `%s` 或 `%(name)s` 占位符绑定。

- `update` 和 `delete` 必须提供非空条件，以避免意外修改整张表。
- `select` 的条件可以省略，代表查询整张表；生产调用应按需要显式添加范围条件。
- 标识符（例如表名、字段名、排序列）不能用值参数占位符绑定，因此只能传入符合约定的标识符。
- 对复杂 JOIN、子查询、数据库特定函数或其他不在上述条件语法内的语句，使用静态、可信 SQL 调用 `execute_query`/`execute_update`，并始终通过独立参数绑定所有值。不得把请求参数、测试数据或其他不可信内容直接插入 SQL 字符串。

## 测试与验证

数据库客户端的自动化测试使用 fake connection/cursor，不需要连接真实 MySQL：

```bash
python -m pytest -q tests/test_database_client.py
```

这些测试验证参数绑定、标识符/条件校验、自动提交、普通事务提交与回滚、只回滚事务、已捕获数据库错误的事务失败标记、游标关闭、连接断开后的重连和嵌套事务拒绝。它们不验证真实 MySQL 服务器版本、表结构或事务隔离级别；这些需要在专用测试数据库环境中单独验证。

## 数据清理责任

客户端不会自动删除成功写入的业务数据。测试用例需要为测试数据使用明确的唯一标识，并在适当的事务或清理阶段删除临时数据。涉及多条写入时，应优先用事务保证失败回滚；若操作本身需要提交后再验证异步业务结果，则必须设计显式且可重试的补偿/清理流程。
