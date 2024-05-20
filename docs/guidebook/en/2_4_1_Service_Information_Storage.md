# Service Information Storage

agentUniverse uses a system-level database to store various types of information generated during application runtime, such as the results of asynchronous service requests, which are stored in this database.

## System Database Configuration
You can configure the system database address in the `config.toml` file:
```toml
[DB]
# A sqlalchemy db uri used for storing various info, for example, service request, generated during application running.
# If it's empty, agentUniverse will create a local sqlite db as default choice.
system_db_uri = ''
```
Please note that this URI should comply with the URI format specification in SQLAlchemy.
When this value is empty, a `DB` folder will be created in the project root directory, and a SQLite DB file named `agent_universe.db` will be created in the folder as the default system database.

## Service Information Table Format
agentUniverse uses the following ORM to store request information:
```text
class RequestORM(Base):
    """SQLAlchemy ORM Model for RequestDO."""
    __tablename__ = 'request_task'
    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(20), nullable=False)
    query = Column(Text)
    session_id = Column(String(50))
    state = Column(String(20))
    result = Column(JSON)
    steps = Column(JSON)
    additional_args = Column(JSON)
    gmt_create = Column(DateTime, default=datetime.datetime.now)
    gmt_modified = Column(DateTime, default=datetime.datetime.now,
                          onupdate=datetime.datetime.now)
```
Where `id` is an auto-incremented primary key, `request_id` is a unique ID for each request, `stat`e represents the execution state of the agent task corresponding to the request, `result` is the execution result, `steps` are the intermediate outputs during the execution process, `session_id` and `additional_args` are reserved fields in the current version.