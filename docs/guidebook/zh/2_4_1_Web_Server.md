# Web Server

AgentUniverse提供了一个基于Gunicorn+Flask的Web Server，您可以通过Web Server中预置的API调用开发完成的Agent服务。

## Web Server启动
您需要在AgentUniverse应用启动后，启动Web Server。  
以下是一种启动的示例写法：
```python
from agentuniverse.agent_serve.web.web_booster import start_web_server
from agentuniverse.base.agentuniverse import AgentUniverse

AgentUniverse().start()
start_web_server()
```

## Windows用户
如果您正在windows上使用AgentUniverse，由于Gunicorn兼容性问题，AgentUniverse会直接运行Flask程序。您可以在`start_web_server`中修改启动端口，如：
```python
from agentuniverse.agent_serve.web.web_booster import start_web_server

start_web_server(bind='127.0.0.1:8888')
```

## Web Server配置
Web Server的配置按照优先度从低到高包含四个层次:`gunicorn`原生默认配置，AgentUniverse默认配置，配置文件配置和启动时配置。其中`gunicorn`的原生默认配置请参考对应版本的`gunicorn`官方文档。

### AgentUniverse默认配置
```python
DEFAULT_GUNICORN_CONFIG = {
    'bind': '127.0.0.1:8000',
    'workers': 5,
    'backlog': 2048,
    'worker_class': 'gthread',
    'threads': 4,
    'timeout': 60,
    'keepalive': 10
}
```
AgentUniverse根据框架的工作特性预先进行了部分参数的配置，您可以通过下面的配置文件或者是启动Web Server时的参数进行修改。

### 配置文件路径
Web Server的配置路径会在AgentUniverse的主配置config.toml中指定。
```toml
[SUB_CONFIG_PATH]
# Gunicorn config file path, an absolute path or a relative path based on the dir where the current config file is located.
gunicorn_config_path = './gunicorn_config.toml'
```
如果该参数为相对路径形式，对应的父目录为主配置config.toml所在目录。

### 配置文件
```toml
[GUNICORN_CONFIG]
bind = '127.0.0.1:8000'
backlog = 2048
worker_class = 'gthread'
threads = 4
workers = 5
timeout = 60
keepalive = 10
```
配置文件以toml格式书写，具体的配置项不局限于上述实例中的内容，您可以参考`gunicorn`的官方文档进行更详细的配置。

### 启动配置
您也可以通过以下方式在启动Web Server时进行配置：
```python
from agentuniverse.agent_serve.web.web_booster import start_web_server

start_web_server(bind="127.0.0.1:8002", threads=4)
```