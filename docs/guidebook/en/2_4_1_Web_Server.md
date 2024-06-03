# Web Server

AgentUniverse provides a web server based on Flask. You can call the developed Agent services through the preset APIs in the web server.

## Web Server Launch
You need to start the web server after launching the AgentUniverse application.
Here is an example of how to launch it:
```python
from agentuniverse.agent_serve.web.web_booster import start_web_server
from agentuniverse.base.agentuniverse import AgentUniverse

AgentUniverse().start()
start_web_server()
```
Flask server default port is 8888，you can change it by edit `bind` param:
```python
from agentuniverse.agent_serve.web.web_booster import start_web_server
from agentuniverse.base.agentuniverse import AgentUniverse

AgentUniverse().start()
start_web_server(bind="127.0.0.1:8002")
```

If you need to configure more details or pursue production stability, you can use Gunicorn as the HTTP server.

## Gunicorn Configuration
You can set Gunicorn as your HTTP server by configuring it in the configuration file as follows:
```toml
[GUNICORN]
activate = 'true'
```

The configuration of the Gunicorn server consists of four levels in order of increasing priority: native Gunicorn default configuration, AgentUniverse default configuration, configuration file settings, and startup configuration. For Gunicorn's native default configuration, please refer to the official documentation for the corresponding version of Gunicorn.

### AgentUniverse Default Configuration
```python
DEFAULT_GUNICORN_CONFIG = {
    'bind': '127.0.0.1:8888',
    'workers': 5,
    'backlog': 2048,
    'worker_class': 'gthread',
    'threads': 4,
    'timeout': 60,
    'keepalive': 10
}
```
AgentUniverse has pre-configured some parameters based on the framework's working characteristics, which you can modify through the configuration file below or parameters when launching the web server.

### Configuration File Path
The configuration path for the web server is specified in AgentUniverse's main configuration file `config.toml`.
```toml
[GUNICORN]
# Gunicorn config file path, an absolute path or a relative path based on the dir where the current config file is located.
gunicorn_config_path = './gunicorn_config.toml'
```
If this parameter is in relative path format, the corresponding parent directory is the directory where the main configuration file config.toml is located.

### Configuration File
```toml
[GUNICORN_CONFIG]
bind = '127.0.0.1:8888'
backlog = 2048
worker_class = 'gthread'
threads = 4
workers = 5
timeout = 60
keepalive = 10
```
The configuration file is written in TOML format, and the specific configuration items are not limited to the content in the example above. You can refer to the official Gunicorn documentation for more detailed configurations.

### Startup Configuration
You can also configure the web server at startup as follows:
```python
from agentuniverse.agent_serve.web.web_booster import start_web_server

start_web_server(bind="127.0.0.1:8002", threads=4)
```