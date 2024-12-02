# Web API

The Web Server of AgentUniverse provides several API interfaces for calling Agent services, allowing developers to call Agent services through web api.

For convenience, let's assume that the Web Server is started on port 8888 locally and has registered an Agent service named `demo_service`：
```yaml
name: 'demo_service'
description: 'A demo service used for explaining.'
agent: 'demo_agent'
metadata:
  type: 'SERVICE'
```
The `demo_agent` accepts a string type input parameter,
and returns a string: `"Your input is {input}."`

## /service_run
This POST interface calls the Agent service in a synchronous manner, and the call will block until the target Agent service returns a result.
An example call is as follows:
```shell
curl -X POST -H "Content-Type: application/json" -d '{"service_id":"demo_service","params":{"input":"Hello!"}}' http://127.0.0.1:8888/service_run
```
The expected return value example is as follows:
```shell
{
        "success": true,
        "result": "Your input is Hello!.",
        "message": null,
        "request_id": "7dd7d737b6b64c3c92addf541e73e97c"
}
```
- **`success`**: Indicates whether the Agent call was successful or not, with values `true` and `false`.。
- **`message`**: When the `success` value is `false`, this value represents the error message, and it is `null` when successful.
- **`result`**: Represents the result of the execution when the Agent call is successful.
- **`request_id`**: A random string, used for a unique request. It can be used in the [/service_run_result](#service_run_result) interface to query the result of the corresponding request.

## /service_run_stream

This POST interface is similar to `/service_run`, and its call method is consistent with it:
```shell
curl -X POST -H "Content-Type: application/json" -d '{"service_id":"demo_service","params":{"input":"Hello!"}}' http://127.0.0.1:8888/service_run_stream
```
However, the return result of the Agent will be returned in a streaming manner:
```text
# agentuniverse.agent_serve_web.flask_server.service_run_stream

response = Response(task.stream_run(), mimetype="text/event-stream")
response.headers['X-Request-ID'] = task.request_id
```
`request_id` will be included in the response header X-Request-ID.

## /service_run_async
This POST interface calls the Agent service in an asynchronous manner. The calling method is as follows:
```shell
curl -X POST -H "Content-Type: application/json" -d '{"service_id":"demo_service","params":{"input":"Hello!"}}' http://127.0.0.1:8888/service_run_async
```
The interface will return immediately:
```shell
{
        "success": true,
        "result": null,
        "message": null,
        "request_id": "7dd7d737b6b64c3c92addf541e73e97c"
}
```
The return result will only contain the success indicating whether the call was successful or not, and the request_id indicating this call.
For the result of the call, you need to use the request_id to query in the [/service_run_result](#service_run_result) interface.

## /service_run_result
This GET interface allows users to check the request status with request_id, an example call is as follows:
```shell
 curl 'http://127.0.0.1:8888/service_run_result?request_id=8e6f17dbe7ff4730a62b4a2914d73c74'
```
The expected return value example is as follows:
```shell
{
  "message":null,
  "request_id":"8e6f17dbe7ff4730a62b4a2914d73c74",
  "result":{
    "result":"Your input is Hello!.",
    "state":"finish",
    "steps":[]
    },
  "success":true}

```
The `result` contains three parts: `result` indicates the result of the Agent service execution, `state` indicates the state of the Agent service execution, and `steps` indicates the intermediate process of the Agent service execution.  
`state` represents the task status and includes the following scenarios:
```text
# agentuniverse.agent_serve.web.request_task.TaskStateEnum

class TaskStateEnum(Enum):
    """All possible state of a web request task."""
    INIT = "init"
    RUNNING = "running"
    FINISHED = "finished"
    FAIL = "fail"
    CANCELED = "canceled"
```
