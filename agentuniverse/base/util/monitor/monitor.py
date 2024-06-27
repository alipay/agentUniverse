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

from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.config.configer import Configer

LLM_INVOCATION_SUBDIR = "llm_invocation"


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

    def _get_or_create_subdir(self, subdir: str) -> str:
        """Get or create a subdirectory if it doesn't exist in the monitor directory."""
        path = os.path.join(self.dir, subdir)
        os.makedirs(path, exist_ok=True)
        return path
