# Service

AgentUniverse allows developers to register completed Agents as a Service using a simple template definition. This enables the use of the corresponding Agent services through Web API calls after launching the built-in web server.

## Registration Method

### Step1: Configure Scan Path
AgentUniverse automatically registers Service configuration files by scanning configured paths at application startup. The scanning paths are configured in the `config.toml` file:
```toml
[CORE_PACKAGE]
default = ['default_scan_path']
service = ['service_scan_path']
```
By default, AgentUniverse scans all paths under default or service, with the path configuration under service having higher priority than default.


### Step2: Configuration File
```yaml
name: 'service_name'
description: 'description of the service'
agent: 'agent_name'
metadata:
  type: 'SERVICE'
```
- **`name`**: The name of the Service, which needs to be provided when calling the service through the Web API.
- **`description`**: Description of the Service's functionality.
- **`agent`**: The name of the Agent. For more information about Agents, please refer to [Agent]().
- **`metadata`**: Indicates that this configuration is for a Service; no changes are needed.

## Usage
Please refer to [Web API](2_4_1_Web_Api.md).