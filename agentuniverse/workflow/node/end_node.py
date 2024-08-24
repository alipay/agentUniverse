# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/21 18:46
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: end_node.py
from typing import List

from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.node import Node, NodeData
from agentuniverse.workflow.node.node_config import EndNodeInputParams, NodeInputParams, NodeOutputParams
from agentuniverse.workflow.node.node_output import NodeOutput
from agentuniverse.workflow.workflow_output import WorkflowOutput


class EndNodeData(NodeData):
    inputs: EndNodeInputParams


class EndNode(Node):
    """The basic class of the tool node."""
    _data_cls = EndNodeData

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = NodeEnum.END

    def _run(self, workflow_output: WorkflowOutput) -> NodeOutput:
        inputs: EndNodeInputParams = self._data.inputs
        input_params: List[NodeInputParams] = inputs.input_param
        output_params: List[NodeOutputParams] = self._data.outputs

        input_param = input_params[0]
        input_value = input_param.value

        if input_value.type == 'reference':
            reference_node_id = input_value.content[0]
            reference_output_params: List[NodeOutputParams] = workflow_output.workflow_parameters.get(
                int(reference_node_id), [])
            referenced_value = next(
                (param.value for param in reference_output_params if param.name == input_value.content[1]),
                None
            )
            output_params[0].value = referenced_value
        else:
            output_params[0].value = input_value.content
        workflow_output.workflow_parameters[self.id] = output_params
        workflow_output.workflow_end_params = output_params
        return NodeOutput(node_id=self.id, status=NodeStatusEnum.SUCCEEDED, result=output_params)
