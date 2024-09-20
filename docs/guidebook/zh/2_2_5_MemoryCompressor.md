# MemoryCompressor
MemoryCompressor负责在记忆组件的裁剪记忆流程中，对裁剪的记忆进行压缩总结，合成满足token数限制的最终记忆信息。

MemoryCompressor定义如下：

```python
from typing import Optional, List

from agentuniverse.agent.memory.message import Message
from agentuniverse.base.component.component_base import ComponentEnum
from agentuniverse.base.component.component_base import ComponentBase

class MemoryCompressor(ComponentBase):
    name: Optional[str] = None
    description: Optional[str] = None
    compressor_prompt_version: Optional[str] = None
    compressor_llm_name: Optional[str] = None
    component_type: ComponentEnum = ComponentEnum.MEMORY_COMPRESSOR

    def compress_memory(self, new_memories: List[Message], max_tokens: int = 500, existing_memory: str = '',
                        **kwargs) -> str:
        # omitted code
        pass
```
MemoryCompressor提供了默认的记忆压缩方法，用户在自定义的MemoryCompressor子类中，可以选择性的重写`compress_memory`函数。

在编写完对应代码后，可以参考下面的yaml将MemoryCompressor注册为aU组件：
```yaml
name: 'demo_memory_compressor'
description: 'demo memory compressor'
compressor_prompt_version: 'xxx'
compressor_llm_name: 'openai_llm'
metadata:
  type: 'MEMORY_COMPRESSOR'
  module: 'agentuniverse.agent.memory.memory_compressor.memory_compressor'
  class: 'MemoryCompressor'
```
其中metadata的type必须为MEMORY_COMPRESSOR

### 关注您定义的MEMORY_COMPRESSOR所在的包路径
在agentUniverse项目的config.toml中需要配置MEMORY_COMPRESSOR配置对应的package, 请再次确认您创建的文件所在的包路径是否在`CORE_PACKAGE`中`memory_compressor`路径或其子路径下。

以示例工程中的配置为例，如下：
```yaml
[CORE_PACKAGE]
memory_compressor = ['sample_standard_app.app.core.memory_compressor']
```

## agentUniverse目前内置有以下MemoryCompressor:
### [default_memory_compressor](../../../agentuniverse/agent/memory/memory_compressor/default_memory_compressor.yaml)
组件配置文件如下：
```yaml
name: 'default_memory_compressor'
description: 'default memory compressor'
compressor_prompt_version: 'chat_memory.summarizer_cn'
compressor_llm_name: 'default_qwen_llm'
metadata:
  type: 'MEMORY_COMPRESSOR'
  module: 'agentuniverse.agent.memory.memory_compressor.memory_compressor'
  class: 'MemoryCompressor'
```