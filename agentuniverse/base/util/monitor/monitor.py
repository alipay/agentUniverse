# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/20 16:24
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: monitor.py
import datetime
import json
import os
from typing import Union, Optional

from pydantic import BaseModel

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.config.configer import Configer

LLM_INVOCATION_SUBDIR = "llm_invocation"
AGENT_INVOCATION_SUBDIR = "agent_invocation"


@singleton
class Monitor(BaseModel):
    dir: Optional[str] = './monitor'
    activate: Optional[bool] = False

    def __init__(self, configer: Configer = None, **kwargs):
        super().__init__(**kwargs)
        if configer:
            config: dict = configer.value.get('MONITOR', {})
            self.dir = config.get('dir', './monitor')
            self.activate = config.get('activate', False)

    def trace_llm_invocation(self, source: str, llm_input: Union[str, dict], llm_output: Union[str, dict]) -> None:
        """Trace the llm invocation and save it to the monitor jsonl file."""
        if self.activate:
            try:
                import jsonlines
            except ImportError:
                raise ImportError(
                    "jsonlines is required to trace llm invocation: `pip install jsonlines`"
                )
            # get the current time
            date = datetime.datetime.now()
            llm_invocation = {
                "source": source,
                "date": date.strftime("%Y-%m-%d %H:%M:%S"),
                "llm_input": llm_input,
                "llm_output": llm_output,
            }
            # files are stored in hours
            filename = f"llm_{date.strftime('%Y-%m-%d-%H')}.jsonl"
            # file path to save
            path_save = os.path.join(str(self._get_or_create_subdir(LLM_INVOCATION_SUBDIR)), filename)

            # write to jsonl
            with jsonlines.open(path_save, 'a') as writer:
                writer.write(llm_invocation)

    def trace_agent_invocation(self, source: str, agent_input: Union[str, dict],
                               agent_output: Union[str, dict]) -> None:
        """Trace the agent invocation and save it to the monitor jsonl file."""
        if self.activate:
            try:
                import jsonlines
            except ImportError:
                raise ImportError(
                    "jsonlines is required to trace llm invocation: `pip install jsonlines`"
                )
            # get the current time
            date = datetime.datetime.now()
            agent_invocation = {
                "source": source,
                "date": date.strftime("%Y-%m-%d %H:%M:%S"),
                "agent_input": self.serialize_obj(agent_input),
                "agent_output": self.serialize_obj(agent_output),
            }
            # files are stored in hours
            filename = f"agent_{source}_{date.strftime('%Y-%m-%d-%H')}.jsonl"
            # file path to save
            path_save = os.path.join(str(self._get_or_create_subdir(AGENT_INVOCATION_SUBDIR)), filename)

            # write to jsonl
            with jsonlines.open(path_save, 'a') as writer:
                writer.write(agent_invocation)

    def _get_or_create_subdir(self, subdir: str) -> str:
        """Get or create a subdirectory if it doesn't exist in the monitor directory."""
        path = os.path.join(self.dir, subdir)
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def default_serializer(obj):
        """Default serializer for objects."""
        if isinstance(obj, InputObject):
            return obj.to_dict()
        elif isinstance(obj, OutputObject):
            return obj.to_dict()
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    def serialize_obj(self, obj):
        """Serialize an object and filter out non-serializable values."""
        filtered_obj = self.filter_and_serialize(obj)
        return json.loads(json.dumps(filtered_obj, default=self.default_serializer))

    def filter_and_serialize(self, obj):
        """Recursively filter out non-serializable values from an object."""

        def is_json_serializable(value):
            """Check if value is a JSON serializable object."""
            try:
                json.dumps(value, default=self.default_serializer)
                return True
            except (TypeError, OverflowError):
                return False

        def filter_dict(d):
            return {k: v for k, v in d.items() if is_json_serializable(v)}

        def recursive_filter(o):
            if isinstance(o, dict):
                return filter_dict({k: recursive_filter(v) for k, v in o.items()})
            elif isinstance(o, list):
                return [recursive_filter(i) for i in o if is_json_serializable(i)]
            else:
                return o

        return recursive_filter(obj)
