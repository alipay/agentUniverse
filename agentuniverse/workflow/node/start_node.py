# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/21 15:01
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: start_node.py
from typing import Optional, Dict

from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.node_output import NodeOutput
from agentuniverse.workflow.node.node import Node


class StartNode(Node):
    """The basic class of the tool node."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = NodeEnum.START

    def _run(self, workflow_parameters: Optional[Dict[int, Dict]]) -> NodeOutput:
        input_parameters = self._data.input_parameters
        output_parameters = self._data.output_parameters

        if len(input_parameters) != len(output_parameters):
            raise ValueError("StartNode: Mismatch in number of input and output parameters.")

        output_params = {}
        for in_param, out_param in zip(input_parameters, output_parameters):
            if in_param.value is None:
                raise ValueError(f"Input parameter {in_param.name} cannot be None.")
            output_params[out_param.name] = in_param.value

        workflow_parameters[self.id] = output_params
        return NodeOutput(status=NodeStatusEnum.SUCCEEDED, result=output_params)
