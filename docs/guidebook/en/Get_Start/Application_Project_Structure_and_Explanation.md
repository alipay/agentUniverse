# Application Project Structure and Explanation
As you can see, `agentUniverse`  is designed with lightweight and integration capabilities in mind, allowing you to incorporate `agentUniverse`  into any of your projects for seamless operation.

## Recommended Project Directory Structure and Explanation
The directory structure provided below is only a suggestion, and you are free to adjust it according to your preferences and actual situation. We will explain this in more detail later in the document.

```
/
├── app/
│   ├── biz/
│   ├── bootstarp/
│   │   └── server_application.py
│   ├── core/
│   │   ├── agent
│   │   ├── knowledge
│   │   ├── llm
│   │   ├── memory
│   │   ├── planner
│   │   ├── service
│   │   └── tool
│   ├── test/
│   └── web/
├── config
├── pyproject.toml
└── other project files...
```

Here's what each package directory level means:
* app - The main application program code
  * biz - Your business code, where you can organize subdirectories as needed
  * bootstrap - The entry layer for starting the web server, for starting details refer to server_application.py
  * core - The core layer of LLM agent application components
    * agent - Place the agents you build
    * knowledge - The knowledge you customize and use
    * llm - The LLM (Language Model) you customize and use
    * memory - The memory sysytem you customize and use
    * planner - The collaborative mode you customize and use
    * service - Directory for service registration
    * tool - The tools you customize and use
  * test - Directory for tests
  * web - TThe web layer, currently left empty for future development 
* config - Application configuration code

## Using Any Project Directory Structure
You can adjust the project directory structure according to your preferences and actual circumstances, but please ensure you follow the rules below.

### Bootstrap Startup Directory
Regardless of the location of your project's startup script, except for testing, you should start the application service with the following statement:

```python
from agentuniverse.agent_serve.web.web_booster import start_web_server
from agentuniverse.base.agentuniverse import AgentUniverse


class ServerApplication:
    """
    Server application.
    """

    @classmethod
    def start(cls):
        AgentUniverse().start()
        start_web_server()

ServerApplication.start()

```
`ServerApplication.start()` is the server startup method for this framework, which accepts a configuration path `config_path` as an input parameter. The default `config_path` points to a file named 'config.toml', located in the config directory under the project root path(`project_root_dir/config/config.toml`). Ensure that the config file path is correct; if you have further changed the directory of the config file, adjust the `config_path` accordingly.

### Config Directory
As mentioned in the [Bootstrap Startup Directory](#bootstrap-startup-directory), the default config path for the project is `project_root_dir/config/config.toml`. If you have made any adjustments to this, please ensure that the correct config file path is provided to the startup method when the application server is launched.

### Core Directory
The core directory, as recommended in the project's directory structure, is primarily used for placing custom domain components like agents, knowledge bases, LLMs, and other related items. You are free to place all core components wherever you like and not limited to the same main package. You only need to specify the core package path in the `[CORE_PACKAGE]` section of the main configuration file `config/config.toml`.
 
```toml
[CORE_PACKAGE]
# Perform a full component scan and registration for all the paths under this list.
default = ['sample_standard_app.app.core']
# Scan and register agent components for all paths under this list, with priority over the default.
agent = ['sample_standard_app.app.core.agent']
# Scan and register agent components for all paths under this list, with priority over the default.
knowledge = ['sample_standard_app.app.core.knowledge']
# Scan and register knowledge components for all paths under this list, with priority over the default.
llm = ['sample_standard_app.app.core.llm']
# Scan and register llm components for all paths under this list, with priority over the default.
planner = ['sample_standard_app.app.core.planner']
# Scan and register planner components for all paths under this list, with priority over the default.
tool = ['sample_standard_app.app.core.tool']
# Scan and register memory components for all paths under this list, with priority over the default.
memory = ['sample_standard_app.app.core.memory']
# Scan and register service components for all paths under this list, with priority over the default.
service = ['sample_standard_app.app.core.service']
# Scan and register prompt components for all paths under this list, with priority over the default.
prompt = []
```
The format for specifying package paths in the configuration follows the standard Python package path format. The framework will register, scan, and manage all types of component packages uniformly based on the defined package paths during startup.

**Tips**: The package path should be specified relative to one level below your project's root directory. For example, in the sample_standard_app project, since the package path is specified under the project's top-level directory, it starts with sample_standard_app. If you are using sample_standard_app as a project template and organizing your components under an app subdirectory, then the package path should start with app.xxx.”