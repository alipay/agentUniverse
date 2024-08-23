# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/20 19:42
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: node.py
from abc import abstractmethod
from typing import Optional, Dict, List

from pydantic import BaseModel

from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.node_output import NodeOutput
from agentuniverse.workflow.workflow_config import ParameterConfig


class NodeData(BaseModel):
    input_parameters: List[ParameterConfig]
    output_parameters: List[ParameterConfig]


class Node(BaseModel):
    """The basic class of the node."""

    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    type: NodeEnum = None
    workflow_id: Optional[str] = None
    _data: Optional[NodeData] = None
    _data_cls = NodeData

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._data = self._data_cls(**kwargs.get('data', {}))

    @abstractmethod
    def _run(self, workflow_parameters: Optional[Dict[int, Dict]]) -> NodeOutput:
        raise NotImplementedError

    def run(self, workflow_parameters: Optional[Dict[int, Dict]]) -> NodeOutput:
        try:
            result = self._run(workflow_parameters)
            return result
        except Exception as e:
            return NodeOutput(status=NodeStatusEnum.FAILED, error=str(e))
