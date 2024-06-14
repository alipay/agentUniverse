# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/14 17:32
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: model_node_base.py
import json

from agentuniverse_data.node.enum.enum import NodeEnum
from agentuniverse_data.node.base.node_base import NodeBase


class ModelNodeBase(NodeBase):
    """The ModelNodeBase class, which is used to define the base class of model node."""

    # a json line in jsonl for msg between nodes
    _param_in_json_obj: json = None
    _platform_mode_is_pro: bool = False

    def __init__(self):
        super().__init__(node_type=NodeEnum.MODEL)

    def _node_preprocess(self) -> None:
        super()._node_preprocess()
        if self._param_in_handler:
            self._param_in_json_obj = self._param_in_handler.read_json_obj()

    def _node_process(self) -> None:
        pass

    def _node_postprocess(self) -> None:
        super()._node_postprocess()
        if self._param_in_json_obj and self._param_out_handler:
            self._param_out_handler.write_json_obj(self._param_in_json_obj)
