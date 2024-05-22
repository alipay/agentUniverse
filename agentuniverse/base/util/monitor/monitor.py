# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/20 16:24
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: monitor.py
import datetime
import json
import jsonlines
import os
from typing import Union

from pydantic import BaseModel

from agentuniverse.base.annotation.singleton import singleton

LLM_INVOCATION_SUBDIR = "llm_invocation"


@singleton
class Monitor(BaseModel):
    dir: str = "./monitor"

    def trace_llm_invocation(self, source: str, llm_input: Union[str, dict], llm_output: Union[str, dict]) -> None:
        """Trace the llm invocation and save it to the monitor jsonl file."""
        # get current time
        date = datetime.datetime.now()
        llm_invocation = {
            "source": source,
            "date": date.strftime("%Y%m%d-%H%M%S"),
            "llm_input": llm_input,
            "llm_output": llm_output,
        }
        filename = f"llm_{date.strftime('%Y%m%d-%H')}.jsonl"
        # file path to save
        path_save = os.path.join(str(self._get_or_create_subdir(LLM_INVOCATION_SUBDIR)), filename)

        # write to jsonl
        with jsonlines.open(path_save, 'a') as writer:
            json_record = json.dumps(llm_invocation, ensure_ascii=False)
            writer.write(json_record)

    def _get_or_create_subdir(self, subdir: str) -> str:
        """Get or create a subdirectory if it doesn't exist in the monitor directory."""
        path = os.path.join(self.dir, subdir)
        os.makedirs(path, exist_ok=True)
        return path
