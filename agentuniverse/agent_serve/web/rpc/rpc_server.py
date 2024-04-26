# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/19 15:59
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: rpc_server.py

import json

from agentuniverse.agent_serve.service_instance import ServiceInstance
from ..request_task import RequestTask
from ..web_util import service_run_queue

# TODO: RPC Agent Service API.


def service_run(saved: bool, params: str, service_id: str):
    if params and params.strip():
        params = json.loads(params)
    else:
        params = {}
    request_task = RequestTask(ServiceInstance(service_id).run, saved,
                               **params)
    result = request_task.run()
    return {
        "success": True,
        "result": result,
        "message": None,
        "request_id": request_task.request_id
    }


def service_run_async(saved: bool, params: str, service_id: str):
    if params and params.strip():
        params = json.loads(params)
    else:
        params = {}
    params['service_id'] = service_id
    task = RequestTask(service_run_queue, saved, **params)
    task.async_run()
    return {
        "success": True,
        "result": None,
        "message": None,
        "request_id": task.request_id
    }
