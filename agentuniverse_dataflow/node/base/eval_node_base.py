# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/14 17:31
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: eval_node_base.py
from agentuniverse_dataflow.node.enum.enum import NodeEnum
from agentuniverse_dataflow.node.base.node_base import NodeBase


class EvalNodeBase(NodeBase):
    """The EvalNodeBase class, which is used to define the base class of eval node."""

    def __init__(self):
        super().__init__(node_type=NodeEnum.EVAL)

    def _node_process(self) -> None:
        pass
