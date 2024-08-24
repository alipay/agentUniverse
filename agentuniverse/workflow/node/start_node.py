# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/21 15:01
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: start_node.py
from typing import List

from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.node_config import NodeOutputParams
from agentuniverse.workflow.node.node_output import NodeOutput
from agentuniverse.workflow.node.node import Node
from agentuniverse.workflow.workflow_output import WorkflowOutput


class StartNode(Node):
    """The basic class of the tool node."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = NodeEnum.START

    def _run(self, workflow_output: WorkflowOutput) -> NodeOutput:
        start_params: dict = workflow_output.workflow_start_params
        output_params: List[NodeOutputParams] = self._data.outputs
        for output_param in output_params:
            if output_param.name in start_params:
                output_param.value = start_params[output_param.name]
        workflow_output.workflow_parameters[self.id] = output_params
        return NodeOutput(node_id=self.id, status=NodeStatusEnum.SUCCEEDED, result=output_params)
