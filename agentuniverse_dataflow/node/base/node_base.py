# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/14 17:06
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: node_base.py
from abc import abstractmethod
import json
from typing import Any, List, Dict, Optional

from pydantic import BaseModel

from agentuniverse_dataflow.node.enum.enum import NodeEnum
from agentuniverse_dataflow.util.fileio.node_msg_jsonl import JsonFileWriter, JsonFileReader


class NodeBase(BaseModel):
    """The NodeBase class, which is used to define the base class of node."""

    node_type: NodeEnum = None
    _is_flow_start_node: bool = False

    # jsonl message between nodes
    param_in_jsonl: str = None
    datasets_in_jsonl: List[str] = None
    param_out_jsonl: str = None
    dataset_out_jsonl: str = None

    llm: str = None
    prompt_version: str = None

    node_param_json: Dict[str, Any] = None

    _param_in_handler: Any = None
    _param_out_handler: Any = None
    _dataset_in_handler: Any = None
    _dataset_out_handler: Any = None

    def set_flow_start_node(self) -> None:
        self._is_flow_start_node = True

    def set_param_in_jsonl(self, param_in_jsonl: str) -> None:
        self.param_in_jsonl = param_in_jsonl

    def set_param_out_jsonl(self, param_out_jsonl: str) -> None:
        self.param_out_jsonl = param_out_jsonl

    def set_datasets_in_jsonl(self, datasets_in_jsonl: list[str]) -> None:
        self.datasets_in_jsonl = datasets_in_jsonl

    def set_dataset_out_jsonl(self, dataset_out_jsonl: str) -> None:
        self.dataset_out_jsonl = dataset_out_jsonl

    def set_node_param_json(self, node_param_json: json) -> None:
        if node_param_json:
            self.node_param_json = node_param_json

    def set_llm(self, llm: str) -> None:
        if llm:
            self.llm = llm

    def set_prompt_version(self, prompt_version: str) -> None:
        if prompt_version:
            self.prompt_version = prompt_version

    def _node_preprocess(self) -> None:
        if self.param_in_jsonl:
            self._param_in_handler = JsonFileReader(self.param_in_jsonl)
        # init the first dataset as default
        if self.datasets_in_jsonl and len(self.datasets_in_jsonl) > 0:
            self._dataset_in_handler = JsonFileReader(self.datasets_in_jsonl[0])
        if self.param_out_jsonl:
            self._param_out_handler = JsonFileWriter(self.param_out_jsonl)
        if self.dataset_out_jsonl:
            self._dataset_out_handler = JsonFileWriter(self.dataset_out_jsonl)

    @abstractmethod
    def _node_process(self) -> None:
        pass

    def _node_postprocess(self) -> None:
        pass

    def execute(self) -> None:

        self._node_preprocess()
        self._node_process()
        self._node_postprocess()

    def _get_node_param(self, key: str, default=None) -> Optional[any]:
        if self.node_param_json:
            if key in self.node_param_json:
                return self.node_param_json.get(key)

        return default
