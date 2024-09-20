# MemoryStorage
MemoryStorage负责在记忆组件中，做记忆的临时/持久化存储。

MemoryStorage定义如下：

```python
from typing import Optional, List

from agentuniverse.agent.memory.message import Message
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum

class MemoryStorage(ComponentBase):
    name: Optional[str] = None
    description: Optional[str] = None
    component_type: ComponentEnum = ComponentEnum.MEMORY_STORAGE
    
    def add(self, message_list: List[Message], session_id: str = '', agent_id: str = '', **kwargs) -> None:
        pass

    def delete(self, session_id: str = None, agent_id: str = None, **kwargs) -> None:
        pass

    def get(self, session_id: str = '', agent_id: str = '', top_k=10, **kwargs) -> List[Message]:
        pass
```
用户在自定义的MemoryStorage子类中，需要重写add/delete/get函数，完成对记忆信息的存储/删除/获取。

在编写完对应代码后，可以参考下面的yaml将MemoryStorage注册为aU组件：
```yaml
name: 'chroma_memory_storage'
description: 'demo chroma memory storage'
collection_name: 'memory'
persist_path: '../../DB/memory.db'
embedding_model: 'dashscope_embedding'
metadata:
  type: 'MEMORY_STORAGE'
  module: 'agentuniverse.agent.memory.memory_storage.chroma_memory_storage'
  class: 'ChromaMemoryStorage'
```
其中metadata的type必须为MEMORY_STORAGE

### 关注您定义的MEMORY_STORAGE所在的包路径
在agentUniverse项目的config.toml中需要配置MEMORY_STORAGE配置对应的package, 请再次确认您创建的文件所在的包路径是否在`CORE_PACKAGE`中`memory_storage`路径或其子路径下。

以示例工程中的配置为例，如下：
```yaml
[CORE_PACKAGE]
memory_storage = ['sample_standard_app.app.core.memory_storage']
```

## agentUniverse目前内置有以下MemoryStorage组件:
### [local_memory_storage](../../../agentuniverse/agent/memory/memory_storage/local_memory_storage.py)
系统内置组件配置文件如下：
```yaml
name: 'local_memory_storage'
description: 'local memory storage'
metadata:
  type: 'MEMORY_STORAGE'
  module: 'agentuniverse.agent.memory.memory_storage.local_memory_storage'
  class: 'LocalMemoryStorage'
```
### [chroma_memory_storage](../../../agentuniverse/agent/memory/memory_storage/chroma_memory_storage.py)
**示例**组件配置文件如下：
```yaml
name: 'chroma_memory_storage'
description: 'demo chroma memory storage'
collection_name: 'memory'
persist_path: '../../DB/memory.db'
embedding_model: 'dashscope_embedding'
metadata:
  type: 'MEMORY_STORAGE'
  module: 'agentuniverse.agent.memory.memory_storage.chroma_memory_storage'
  class: 'ChromaMemoryStorage'
```
其中`collection_name`为chroma的collection名称，`persist_path`为chroma的持久化路径，`embedding_model`为用于向量检索的embedding领域组件名称。

### [sql_alchemy_memory_storage](../../../agentuniverse/agent/memory/memory_storage/sql_alchemy_memory_storage.py)
**示例**组件配置文件如下：
```yaml
name: 'mysql_memory_storage'
description: 'demo mysql memory storage'
sqldb_table_name: 'memory'
sqldb_wrapper_name: 'mysql_sqldb_wrapper'
metadata:
  type: 'MEMORY_STORAGE'
  module: 'agentuniverse.agent.memory.memory_storage.sql_alchemy_memory_storage'
  class: 'SqlAlchemyMemoryStorage'
```
其中`sqldb_table_name`为sqlalchemy的table名称，`sqldb_wrapper_name`为agentUniverse的sqldb领域组件名称。

mysql_sqldb_wrapper的示例配置如下：
```yaml
name: 'mysql_sqldb_wrapper'
description: 'mysql_sqldb_wrapper'
db_uri: "mysql+pymysql://root:root123456@127.0.0.1:3306/test"
engine_args:
  pool_size: 5
metadata:
  type: 'SQLDB_WRAPPER'
```