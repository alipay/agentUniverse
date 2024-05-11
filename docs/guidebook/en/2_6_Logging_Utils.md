# Logging Utils

The log component of AgentUniverse is implemented based on loguru, providing a well-packaged global log component and customizable log components. This tutorial will first introduce the usage of the log configuration file in AgentUniverse, then explain the usage of the global log component and customizable log components in turn, and finally describe how to interface with external log service components.
    
## Log Configuration

### Configuration File Path
The configuration path of the log file is specified in the main configuration of AgentUniverse, config.toml.
```toml
[SUB_CONFIG_PATH]
# Log config file path, an absolute path or a relative path based on the dir where the current config file is located.
log_config_path = './log_config.toml'
```
 If this parameter is a relative path, its parent directory is the directory where the main configuration file, config.toml, is located.
If this parameter does not exist, AgentUniverse will use the default log configuration, see [default configuration](#default-configuration).

### Configuration File Options
The configuration file for logs is in the toml file format; an example configuration is as follows:
```toml
[LOG_CONFIG]
[LOG_CONFIG.BASIC_CONFIG]
log_level = "INFO"
log_path = "~/.agent_universe_log"
log_rotation = "100 MB"
log_retention = "7 days"
```
- **`log_level`**: The default log level, possible values include "TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL". The level of the global log component will be the same as this value. When creating a custom log component, if log level is not specified, this default level will be used.
- **`log_path`**: The log storage path, if this value is empty, a {workdir}/../../logs folder will be created as the log storage path.
- **`log_rotation`**: This parameter accepts a duration (e.g., "1 week") or file size (e.g., "100 MB"), indicating the condition for log file rotation.
- **`log_retention`**: This parameter accepts a duration (e.g., "7 days") indicating the retention period for old log files, which will be deleted after they expire.

### Default Configuration
Configuration not specified in the log configuration file will take the following default settings:
- **`log_level`**: "INFO"
- **`log_rotation`**: "10MB"
- **`log_retention`**: "3 days"

Two default log files, `afaf_all.log` and `afaf_error.log`, will be located in the log storage path. 'All' records all logs above the default log level set in the log configuration, while 'error' records only logs at the ERROR level and above. The format for log component output is:
```python
log_format: str = ("<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
                       "| <level>{level: <8}</level> "
                       "| {extra[context_prefix]} "
                       "| <cyan>{name}</cyan>"
                       ":<cyan>{function}</cyan>"
                       ":<cyan>{line}</cyan> "
                       "| <level>{message}</level>")
```
Where `{extra[context_prefix]}` defaults to `default`, When `LOG_CONTEXT` exists in the framework context, its contents will be replaced by the contents of `LOG_CONTEXT`. For more information related to the framework context, please refer to  [Framework_Context](2_7_Framework_Context.md)。

## Global Log Component
AgentUniverse provides a directly usable log component `logging_util.Logger`, which you can introduce into your project as follows:
```python
from agentuniverse.base.util.logging.logging_util import LOGGER
```
You can use this object's different member functions to record logs of different levels:
```python
from agentuniverse.base.util.logging.logging_util import LOGGER

LOGGER.info("This is an info log.")
LOGGER.debug("This is a debug log.")
LOGGER.warn("This is a warn log.")
LOGGER.error("This is an error log.")
```

## Custom Log Components
If you want to output and save certain logs separately, you can create a custom log component using the `get_module_logger` function::
```python
from agentuniverse.base.util.logging.logging_util import get_module_logger
new_logger = get_module_logger("new_module")
```
Logs recorded by this new component will be saved in the log storage path, in a log file named `afaf_{module_name}.log`,  where `{module_name}` is the module name you passed into `get_module_logger`, as in the example above, the corresponding file would be `afaf_new_module.log`.

## External Log Service

If you want to use more log utils, please refer to [extension logging utils](3_1_Extension_Logging_Utils.md).
