# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/20 20:01
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: tool_node.py
from typing import Optional, Dict

from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.node import NodeData, Node
from agentuniverse.workflow.node.node_output import NodeOutput


class ToolNodeData(NodeData):
    id: str


class ToolNode(Node):
    """The basic class of the tool node."""
    _data_cls = ToolNodeData

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = NodeEnum.TOOL

    def _run(self, workflow_parameters: Optional[Dict[int, Dict]]) -> NodeOutput:
        tool_id = self._data.id
        tool = ToolManager().get_instance_obj(tool_id)
        if tool is None:
            raise ValueError("No tool with id {} was found.".format(tool_id))
        input_parameters = self._data.input_parameters

        intput_params = {}
        for input_parameter in input_parameters:
            if input_parameter.value is not None:
                intput_params[input_parameter.name] = input_parameter.value
                continue
            if input_parameter.selector is None:
                raise ValueError(f"Input parameter {input_parameter.name} selector cannot be None.")
            node_id = input_parameter.selector[0]


            input_parameter.value = workflow_parameters[input_parameter.id][input_parameter.name]

        output_parameters = self._data.output_parameters
        output_params = {}
        for i in range(len(input_parameters)):
            if input_parameters[i].value is None:
                raise ValueError("Input parameter {} cannot be None.".format(input_parameters[i].name))
            output_params[output_parameters[i].name] = input_parameters[i].value
        workflow_parameters[self.id] = output_params
        return NodeOutput(status=NodeStatusEnum.SUCCEEDED, result=output_params)
