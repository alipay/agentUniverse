# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/14 17:06
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: data_node.py
from agentuniverse_data.node.base.node_base import NodeBase


class DataNodeBase(NodeBase):
    """The DataBase class, which is used to define the base class of data node."""
    _batch_line_size: int = 10
    _batch_prompt_size: int = 40

    def _node_process(self) -> None:
        pass
