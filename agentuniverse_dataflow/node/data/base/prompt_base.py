# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/16 19:19
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: prompt_base.py
from typing import List

from agentuniverse_dataflow.node.enum.enum import NodeEnum
from agentuniverse_dataflow.node.base.data_node_base import DataNodeBase


class PromptBase(DataNodeBase):
    """The PromptNodeBase class, which is used to define the base class of prompt node."""

    _prompt_list: List[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(node_type=NodeEnum.PROMPT)

    def _node_preprocess(self) -> None:
        super()._node_preprocess()

        if self._dataset_in_handler:
            self._prompt_list = self._dataset_in_handler.read_json_prompt_list()

    def _node_postprocess(self) -> None:
        super()._node_postprocess()

        if self._prompt_list and self._dataset_out_handler:
            self._dataset_out_handler.write_json_prompt_list(self._prompt_list)
