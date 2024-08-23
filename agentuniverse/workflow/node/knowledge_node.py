# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/20 20:02
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: knowledge_node.py

from agentuniverse.workflow.node.enum import NodeEnum
from agentuniverse.workflow.node.node import Node, NodeData
from agentuniverse.workflow.workflow_config import RetrivalConfig


class KnowledgeNodeData(NodeData):
    id: str
    retrieval_config: RetrivalConfig


class KnowledgeNode(Node):
    """The basic class of the knowledge node."""
    _data_cls = KnowledgeNodeData

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = NodeEnum.KNOWLEDGE
