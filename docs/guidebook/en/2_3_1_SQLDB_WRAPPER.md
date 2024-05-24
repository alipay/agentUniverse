# SQLDB Wrapper

Based on SQLAlchemy and langchain's SQLDatabase, agentUniverse offers a `SQLDBWrapper` class allowing users to conveniently use most SQL-based databases like SQLite, MySQL, Oracle, etc. For details, please refer to the [SQLAlchemy official website](https://docs.sqlalchemy.org/en/20/dialects/). With SQLDBWrapper, you can easily manage multiple different database connection objects at the same time.

## Registration Method

### Step One: Configure Scan Path
gentUniverse automatically registers the SQLDBWrapper configuration files by scanning the configured paths at application startup. The paths to scan are configured in the `config.toml` file:
```toml
[CORE_PACKAGE]
default = ['default_scan_path']
sqldb_wrapper = ['sqldb_wrapper_scan_path']
```
By default, AgentUniverse scans all paths under `default` or `sqldb_wrapper`, with paths under `sqldb_wrapper` having a higher priority over `default`.


### Step Two: Configuration File
```yaml
name: 'demo_sql'
description: 'demo_sql'
db_uri: "sqlite:///./demo.db"
sql_database_args:
  include_tables: ["users"]
engine_args:
  pool_size: 10
metadata:
  type: 'SQLDB_WRAPPER'
```
- **`name`**: The name of the SQLDBWrapper, used to identify a unique instance.
- **`description`**: A description of the SQLDBWrapper's functionality.
- **`db_uri`**: A SQLAlchemy-style database URI, used to create a SQLAlchemy engine.
- **`sql_database_args`**: Optional parameters for the SQLDatabase class in `LangChain`, for specific details refer to [LangChain's official website](https://python.langchain.com/v0.1/docs/integrations/toolkits/sql_database/).
- **`engine_args`**: Optional parameters, used to configure SQLAlchemy engine parameters. For specific configurable contents, please refer to [SQLAlchemy's webpage](https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine).
- **`metadata`**: Indicates that this configuration is for a `SQLDB_WRAPPER`, no need to change.

## Usage
The SQLDBWrapper class offers the following functions for users:

### run
`run` accepts a `str` type parameter command, representing an SQL statement, and executes this SQL via SQLAlchemy, returning the results. The result is a list, if command is a query statement then the list will contain the query results, each element is a dictionary representing a row in the database, with the key as the column name and the value as the corresponding value.
```python
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager

demo_sqldb_wrapper:SQLDBWrapper = SQLDBWrapperManager().get_instance_obj("demo_sqldb_wrapper")
demo_sqldb_wrapper.run("select * from USERS")
```
Example of returned result:
```text
[{'age': 30, 'id': 1, 'name': 'Alice'}, {'age': 25, 'id': 2, 'name': 'Bob'}]
```

### run_with_str_return
`run_with_str_return` accepts a `str` type parameter command, representing an SQL statement, and executes this SQL via SQLAlchemy, returning the results. The result is a `str`, if command is a query statement then the str consists of all the query results concatenated together, and if the `max_string_length` parameter was configured in `sql_database_args`, the result will be truncated. This function is more convenient for using the results as input for llm.
```python
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager

demo_sqldb_wrapper:SQLDBWrapper = SQLDBWrapperManager().get_instance_obj("demo_sqldb_wrapper")
demo_sqldb_wrapper.run_with_str_return("select * from USERS")
```
Example of returned result:
```text
"[(1, 'Alice', 30), (2, 'Bob', 25)]"
```

### sql_database
If you wish to use some of the native features of SQLAlchemy or SQLDatabase, you can access the corresponding object through the `sql_database` property of SQLDBWrapper:
```python
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager

demo_sqldb_wrapper:SQLDBWrapper = SQLDBWrapperManager().get_instance_obj("demo_sqldb_wrapper")
sql_database_ins = demo_sqldb_wrapper.sql_database
sql_alchemy_engine = sql_database_ins._engine
```