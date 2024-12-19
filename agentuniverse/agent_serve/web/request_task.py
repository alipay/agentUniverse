# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/25 11:18
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: request_task.py
import asyncio
import enum
import traceback
from enum import Enum
import json
import queue
import time
import uuid
from datetime import datetime, timedelta
from threading import Thread
from typing import Optional, AsyncIterator

from .dal.request_library import RequestLibrary
from .dal.entity.request_do import RequestDO
from .thread_with_result import ThreadWithReturnValue
from agentuniverse.base.util.logging.logging_util import LOGGER
from ...agent.output_object import OutputObject

EOF_SIGNAL = '{"type": "EOF"}'


@enum.unique
class TaskStateEnum(Enum):
    """All possible state of a web request task."""
    INIT = "init"
    RUNNING = "running"
    FINISHED = "finished"
    FAIL = "fail"
    CANCELED = "canceled"


# All valid transitions of request task.
VALID_TRANSITIONS = {
    (TaskStateEnum.INIT, TaskStateEnum.RUNNING),
    (TaskStateEnum.INIT, TaskStateEnum.FAIL),
    (TaskStateEnum.INIT, TaskStateEnum.CANCELED),
    (TaskStateEnum.RUNNING, TaskStateEnum.FINISHED),
    (TaskStateEnum.RUNNING, TaskStateEnum.FAIL),
    (TaskStateEnum.RUNNING, TaskStateEnum.CANCELED),
}


class RequestTask:
    """The class that manages the agent service request, including state
    transitions and different types of execution flows."""

    def __init__(self, func, saved=True, **kwargs):
        """Init a RequestTask."""
        self.func: callable = func
        self.kwargs = kwargs
        self.request_id = uuid.uuid4().hex
        self.queue = queue.Queue(maxsize=100)
        self.thread: Optional[ThreadWithReturnValue] = None
        self.state = TaskStateEnum.INIT.value
        # Whether save to Database.
        self.saved = saved
        self.__request_do__ = self.add_request_do()
        self.async_queue = asyncio.Queue(maxsize=200)
        self.async_task = None

    def receive_steps(self):
        """Yield the stream data by getting data from the queue."""
        while True:
            output: str = self.queue.get()
            if output is None:
                break
            if output == EOF_SIGNAL:
                break
            yield "data:" + json.dumps({"process": output},
                                       ensure_ascii=False) + "\n\n"
        if self.canceled():
            return
        try:
            result = self.thread.result()
            if isinstance(result, OutputObject):
                result = result.to_dict()
            yield "data:" + json.dumps({"result": result},
                                       ensure_ascii=False) + "\n\n "
        except Exception as e:
            LOGGER.error("request task execute Fail: " + str(e)+traceback.format_exc())
            yield "data:" + json.dumps({"error": {"error_msg": str(e)}}) + "\n\n "

    async def async_receive_steps(self) -> AsyncIterator[str]:
        while True:
            try:
                output: str = await asyncio.wait_for(self.async_queue.get(), timeout=0.5)
            except asyncio.TimeoutError:
                await asyncio.sleep(1)
                print("Waiting for data timed out. Retrying...")
                continue
            if output is None:
                break
            if output == EOF_SIGNAL:
                break
            yield "data:" + json.dumps({"process": output},
                                       ensure_ascii=False) + "\n\n"
        if self.canceled():
            return
        try:
            result = await self.async_task
            if isinstance(result, OutputObject):
                result = result.to_dict()
            yield "data:" + json.dumps({"result": result},
                                       ensure_ascii=False) + "\n\n"
        except Exception as e:
            LOGGER.error("request task execute Fail: " + str(e))
            yield "data:" + json.dumps({"error": {"error_msg": str(e)}}) + "\n\n"

    def append_steps(self):
        """Tracing async service running state and update it to database."""
        try:
            self.next_state(TaskStateEnum.RUNNING)
            while True:
                output: str = self.queue.get()
                if output is None:
                    break
                if output == EOF_SIGNAL:
                    break
                if output != "" and output != " ":
                    self.__request_do__.steps.append(output)
                if self.saved:
                    RequestLibrary().update_request(self.__request_do__)
            if self.canceled():
                self.__request_do__.result['result'] = {
                    "result": "The task's tracking status has been canceled."}
            else:
                self.__request_do__.result['result'] = self.thread.result()
                self.next_state(TaskStateEnum.FINISHED)
            if self.saved:
                RequestLibrary().update_request(self.__request_do__)
        except Exception as e:
            LOGGER.error("request task update request state Fail: " + str(e))
            self.__request_do__.result['result'] = {"error_msg": str(e)}
            self.next_state(TaskStateEnum.FAIL)
            if self.saved:
                RequestLibrary().update_request(self.__request_do__)

    def async_run(self):
        """Run the service in async mode."""
        self.kwargs['output_stream'] = self.queue
        self.thread = ThreadWithReturnValue(target=self.func,
                                            kwargs=self.kwargs)
        self.thread.start()
        Thread(target=self.append_steps).start()
        Thread(target=self.check_state).start()

    def stream_run(self):
        """Run the service in a separate thread and yield result stream."""
        self.kwargs['output_stream'] = self.queue

        self.thread = ThreadWithReturnValue(target=self.func,
                                            kwargs=self.kwargs)
        self.thread.start()
        return self.receive_steps()

    async def async_stream_run(self) -> AsyncIterator[str]:
        self.kwargs['output_stream'] = self.async_queue
        loop = asyncio.get_event_loop()
        self.async_task = loop.create_task(self.func(**self.kwargs))
        async for item in self.async_receive_steps():
            yield item

    def run(self):
        """Run the service synchronous and return the result."""
        self.next_state(TaskStateEnum.RUNNING)
        try:
            result = self.func(**self.kwargs)
            self.next_state(TaskStateEnum.FINISHED)
            self.__request_do__.result = {"result": result}
            return result
        except Exception as e:
            self.next_state(TaskStateEnum.FAIL)
            self.__request_do__.additional_args['error_msg'] = str(e)
            raise e
        finally:
            if self.saved:
                RequestLibrary().update_request(self.__request_do__)

    def next_state(self, next_state: TaskStateEnum):
        """Update request task state if the transition is valid."""
        if ((TaskStateEnum[self.__request_do__.state.upper()], next_state)
                in VALID_TRANSITIONS):
            self.__request_do__.state = next_state.value
        else:
            raise Exception("Invalid state transition")

    def check_state(self):
        """Keep check request task thread state every minute, if the thread
        is alive, update the request modified time in database."""
        while True:
            if self.thread is not None and self.thread.is_alive():
                LOGGER.debug(
                    "request:" + str(self.request_id) + "task thread alive")
                if self.saved:
                    RequestLibrary().update_gmt_modified(self.request_id)
                time.sleep(60)
                continue
            elif self.__request_do__.state == TaskStateEnum.RUNNING.value:
                # Waiting one minute to avoid skipping the state change step.
                time.sleep(60)
                if self.__request_do__.state == TaskStateEnum.RUNNING.value:
                    LOGGER.debug("request:" + str(self.request_id) +
                                 " task thread stop but state not end")
                    self.__request_do__.state = TaskStateEnum.FAIL.value
                    if self.saved:
                        RequestLibrary().update_request(
                            self.__request_do__)
            break

    def add_request_do(self):
        query_keys = ['question', 'query_content', 'query', 'request', 'input']
        query = next((self.kwargs[key] for key in query_keys if
                      self.kwargs.get(key) is not None),
                     "No relevant query was retrieved.")

        request_do = RequestDO(
            request_id=self.request_id,
            session_id="",
            query=query,
            state=TaskStateEnum.INIT.value,
            result=dict(),
            steps=[],
            additional_args=dict(),
            gmt_create=int(time.time()),
            gmt_modified=int(time.time()),
        )
        if self.saved:
            RequestLibrary().add_request(request_do)
        return request_do

    def result(self):
        """Get the result from service running thread."""
        return self.thread.result()

    @staticmethod
    def is_validate(request_do: RequestDO):
        """If there is no update within ten minutes and the status is neither
        completed nor failed, the task is considered to have failed."""
        if (request_do.gmt_modified < datetime.now() - timedelta(minutes=10)
                and request_do.state != TaskStateEnum.FINISHED.value
                and request_do.state != TaskStateEnum.FAIL.value):
            LOGGER.error("request task is validate fail" + str(request_do))
            request_do.state = TaskStateEnum.FAIL.value
            RequestLibrary().update_request(request_do)

    def cancel(self):
        """Cancel the request task. If a response SSE stream is working, put
        the EOF into the queue."""
        self.next_state(TaskStateEnum.CANCELED)
        if self.queue is not None:
            self.queue.put_nowait(EOF_SIGNAL)

    def request_state(self):
        """Return the request task state."""
        return self.__request_do__.state

    def canceled(self):
        """Whether task is canceled state."""
        return self.__request_do__.state == TaskStateEnum.CANCELED.value

    def finished(self):
        """Set task to finished state."""
        self.__request_do__.state = TaskStateEnum.FINISHED.value

    @staticmethod
    def query_request_state(request_id: str) -> dict | None:
        """Query the request data in database by given request_id.

        Args:
            request_id(str): Unique request id.
        """
        request_do = RequestLibrary().query_request_by_request_id(
            request_id)
        if request_do is None:
            return None
        RequestTask.is_validate(request_do)
        return {
            "state": request_do.state,
            "result": request_do.result,
            "steps": request_do.steps
        }
