# Framework Context

AgentUniverse provides a context management tool that is independent on threads and coroutines level, allowing the storage and retrieval of context variables in a key-value format that need to be managed separately within threads or coroutines.

## Usage

### Creating Context Variables
#### Method 1:
```python
from agentuniverse.base.context.framework_context import FrameworkContext

with FrameworkContext({"context_var1": 1,
                       "context_var2":"context_var"}):
    pass
```
By using the `with` keyword to create a `FrameworkContext` instance, which accepts a `dict` type parameter, AgentUniverse will save all key-value pairs from the parameters to the context manager within the scope of with, and remove them upon exit.

#### Method 2:
```python
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager

FrameworkContextManager().set_context("context_var", "value")
```
Create a new context variable with `FrameworkContextManager` directly. Variables created in this way will exist throughout the lifecycle of the thread or coroutine and can be manually deleted with following code:
```python
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager

FrameworkContextManager().del_context("context_var")
```
### Using Context Variables
You can retrieve previously saved variables through the `FrameworkContextManager`：
```python
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager

FrameworkContextManager().get_context("context_var", default_value=None)
```
The `default_value` is `None` by default. When there is no corresponding key in the context, `default_value` is returned.