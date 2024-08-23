# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/21 18:46
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: end_node.py
from agentuniverse.workflow.node.enum import NodeEnum
from agentuniverse.workflow.node.node import Node


class EndNode(Node):
    """The basic class of the tool node."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = NodeEnum.END
