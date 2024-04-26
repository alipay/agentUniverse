import traceback

from flask import Flask, Response
from werkzeug.exceptions import HTTPException

from ..service_instance import ServiceInstance, ServiceNotFoundError
from .request_task import RequestTask
from .web_util import request_param, service_run_queue, make_standard_response
from ...base.util.logging.logging_util import LOGGER


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route("/echo")
def echo():
    return 'Welcome to agentUniverse!!!'


@app.route("/liveness")
def liveness():
    return make_standard_response(success=True,
                                  result="liveness health check pass!")


@app.route("/service_run", methods=['POST'])
@request_param
def service_run(service_id: str, params: dict, saved: bool = False):
    """Synchronous invocation of an agent service.

    Request Args:
        service_id(`str`): The id of the agent service. Format like
            {appname}.service.{service_name}.
        params(`dict`): Json style params passed to service.
        saved(`bool`): Save the request and result into database.

    Return:
        Returns a dict containing two keys: success and result.
        success: This key holds a boolean value indicating the task was
        successfully or not.
        result: This key points to a nested dictionary that includes the
        result of the task.
    """
    params = {} if params is None else params
    request_task = RequestTask(ServiceInstance(service_id).run, saved, **params)
    result = request_task.run()
    return make_standard_response(success=True, result=result,
                                  request_id=request_task.request_id)


@app.route("/service_run_stream", methods=['POST'])
@request_param
def service_run_stream(service_id: str, params: dict, saved: bool = False):
    """Synchronous invocation of an agent service, return in stream form.

    Request Args:
        service_id(`str`): The id of the agent service. Format like
            {appname}.service.{service_name}.
        params(`dict`): Json style params passed to service.
        saved(`bool`): Save the request and result into database.

    Return:
        A SSE(Server-Sent Event) stream.
    """
    params = {} if params is None else params
    params['service_id'] = service_id
    task = RequestTask(service_run_queue, saved, **params)
    response = Response(task.stream_run(), mimetype="text/event-stream")
    response.headers['X-Request-ID'] = task.request_id
    return response


@app.route("/service_run_async", methods=['POST'])
@request_param
def service_run_async(service_id: str, params: dict, saved: bool = True):
    """Async invocation of an agent service, return the request id used to
    get result later.

    Request Args:
        service_id(`str`): The id of the agent service. Format like
            {appname}.service.{service_name}.
        params(`dict`): Json style params passed to service.
        saved(`bool`): Save the request and result into database.

    Return:
        Returns a dict containing two keys: success and result.
        success: This key holds a boolean value indicating the task was
        successfully or not.
        result: This key points to a dictionary contains a key: request_id,
        its value can be used in service_run_result api to get the result
        of async task.

    Example Response:
        {"success": True, "data": {
        "request_id":"05d0a28785cc455894ebb88bba14a67e"}}.
    """
    params = {} if params is None else params
    params['service_id'] = service_id
    task = RequestTask(service_run_queue, saved, **params)
    task.async_run()
    return make_standard_response(success=True,
                                  request_id=task.request_id)


@app.route("/service_run_result", methods=['GET'])
@request_param
def service_run_result(request_id: str):
    """Get the async service result.

    Request Args:
        request_id(`str`): Request id returned by async run api.

    Return:
        Returns a dict containing two keys: success and result if request_id
        exists in database.
        success: This key holds a boolean value indicating the task was
        successfully or not.
        result: This key points to a nested dictionary that includes the
        result of the task.
    """
    data = RequestTask.query_request_state(request_id)
    if data is None:
        return make_standard_response(
            success=False,
            message=f"request {request_id} not found"
        )
    return make_standard_response(success=True, result=data,
                                  request_id=request_id)


@app.errorhandler(HTTPException)
def handle_http_exception(e):
    """A global exception handler handle flask origin http exceptions."""
    response = e.get_response()
    return response


@app.errorhandler(Exception)
def handle_exception(e):
    """A global non http exception handler"""
    LOGGER.error(traceback.format_exc())
    if isinstance(e, ServiceNotFoundError):
        return make_standard_response(success=False,
                                      message=str(e),
                                      status_code=404)
    return make_standard_response(success=False,
                                  message="Internal Server Error",
                                  status_code=500)
