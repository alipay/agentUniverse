# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/14 17:54
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: dump_base.py
from typing import List, Tuple

from agentuniverse_dataflow.node.base.model_node_base import ModelNodeBase


class DumpBase(ModelNodeBase):
    """The DumpBase class, which is used to define the base class of dump node."""

    _prompt_answer_out_list: List[Tuple[str, str]] = None

    def _node_preprocess(self) -> None:
        super()._node_preprocess()

    def _node_process(self) -> None:
        pass

    def _node_postprocess(self) -> None:
        self._param_in_json_obj = None
        super()._node_postprocess()

        if self._prompt_answer_out_list and self._dataset_out_handler:
            self._dataset_out_handler.write_json_prompt_answer_list(self._prompt_answer_out_list)
