# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/16 19:20
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: prompt_answer_base.py
from typing import List, Tuple

from agentuniverse_dataflow.node.enum.enum import NodeEnum
from agentuniverse_dataflow.node.base.data_node_base import DataNodeBase


class PromptAnswerBase(DataNodeBase):
    """The PromptAnswerNodeBase class, which is used to define the base class of prompt answer node."""

    _prompt_answer_list: List[Tuple[str, str]] = None

    def __init__(self, *args, **kwargs):
        super().__init__(node_type=NodeEnum.PROMPT_ANSWER)

    def _node_preprocess(self) -> None:
        super()._node_preprocess()

        if self._dataset_in_handler:
            self._prompt_answer_list = self._dataset_in_handler.read_json_prompt_answer_list()

    def _node_postprocess(self) -> None:
        super()._node_postprocess()

        if self._prompt_answer_list:
            self._dataset_out_handler.write_json_prompt_answer_list(self._prompt_answer_list)
