## gRPC
In addition to HTTP API, we also provide a built-in GRPC Agent service server.

### Starting gRPC server
If you need to enable GRPC server, you can configure it in the config.toml file as follows:
```toml
[GRPC]
activate = 'true'
max_workers = 10
server_port = 50051
```
- **activate**: The gRPC server starts only when this value is set to `true`.
- **max_workers**: The maximum number of threads in the gRPC server thread pool, with a default of 10.
- **server_port**: The service port of the gRPC server, with a default of 50051.

### Calling the gRPC Service

### Interface Definition
The complete definition file for the gRPC service interface is as follows:
```text
syntax = "proto3";

package agentuniverse;

service AgentUniverseService {
  rpc service_run(AgentServiceRequest) returns (AgentServiceResponse);
  rpc service_run_async(AgentServiceRequest) returns (AgentServiceResponse);
  rpc service_run_result(AgentResultRequest) returns (AgentServiceResponse);
}

message AgentServiceRequest {
  string service_id = 1;
  string params = 2;
  bool saved = 3;
}

message AgentServiceResponse {
  string message = 1;
  bool success = 2;
  string request_id = 3;
  string result = 4;
}

message AgentResultRequest {
    string request_id = 1;
}
```
\
Similar to the [Web API](2_4_1_Web_Api.md), the gRPC service includes three interfaces:
```text
service AgentUniverseService {
  rpc service_run(AgentServiceRequest) returns (AgentServiceResponse);
  rpc service_run_async(AgentServiceRequest) returns (AgentServiceResponse);
  rpc service_run_result(AgentResultRequest) returns (AgentServiceResponse);
}
```
- **service_run**: Synchronously calls an Agent service, blocking during the call until the Agent returns results.
- **service_run_async**: Asynchronously calls an Agent service, initially returning a `request_id`, and the result of the Agent service can be queried later using the `service_run_result` interface with this ID.
- **service_run_result**: Queries the result of the Agent service.。

\
The request body structure for calling an Agent service is as follows:：
```text
message AgentServiceRequest {
  string service_id = 1;
  string params = 2;
  bool saved = 3;
}
```
- **service_id**: The model service id registered in the application.。
- **params**: The service input parameters in JSON String format, which will be parsed by `json.loads` into the form of `**kwargs` passed to the underlying Agent.
- **saved**: Whether to save the result of this request. If the value is `false`, the result of this request cannot be queried in `service_run_result`.

\
The request body structure for querying the result of an Agent service is as follows:
```text
message AgentResultRequest {
    string request_id = 1;
}
```
- **request_id**: The request ID to be queried.

\
The structure of the return result is as follows:
```text
message AgentServiceResponse {
  string message = 1;
  bool success = 2;
  string request_id = 3;
  string result = 4;
}
```
- **message**: Detailed error information when the request fails.
- **success**: Indicates whether the request was successfully executed.
- **request_id**: The ID of this request.
- **result**: The result of executing the Agent service. It is empty in the asynchronous interface `service_run_async`.

### Call Example
```python
import grpc
from agentuniverse.agent_serve.web.rpc.grpc import agentuniverse_service_pb2, \
    agentuniverse_service_pb2_grpc


# Start you server_application first.
def test_run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = agentuniverse_service_pb2_grpc.AgentUniverseServiceStub(channel)
        response = stub.service_run(agentuniverse_service_pb2.AgentServiceRequest(
            service_id='demo_service',
            params='{"input":"(18+3-5)/2*4=?"}',
            saved=True
        ))
        print("client received: " + response.request_id)

        response = stub.service_run_result(agentuniverse_service_pb2.AgentResultRequest(
            request_id=response.request_id
        ))
        print("client received: " + response.result)
```



