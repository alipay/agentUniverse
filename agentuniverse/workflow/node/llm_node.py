# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/20 20:02
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: llm_node.py
import re
from typing import List

from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.node import NodeData, Node
from agentuniverse.workflow.node.node_config import LLMNodeInputParams, NodeOutputParams
from agentuniverse.workflow.node.node_output import NodeOutput
from agentuniverse.workflow.workflow_output import WorkflowOutput


class LLMNodeData(NodeData):
    inputs: LLMNodeInputParams


class LLMNode(Node):
    """The basic class of the llm node."""

    _data_cls = LLMNodeData

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = NodeEnum.LLM

    def _run(self, workflow_output: WorkflowOutput) -> NodeOutput:
        inputs: LLMNodeInputParams = self._data.inputs
        param_dict = {param.name: str(param.value) for param in inputs.llm_param}

        llm_id = param_dict.get('id')
        llm: LLM = LLMManager().get_instance_obj(llm_id)
        if llm is None:
            raise ValueError("No llm with id {} was found.".format(llm_id))

        model_name = param_dict.get('model_name')
        temperature = param_dict.get('temperature')
        prompt = param_dict.get('prompt')

        input_variables = re.findall(r'\{\{(.*?)\}\}', prompt)
        llm.set_by_agent_model(model_name=model_name, temperature=temperature)

        llm_input_params = self._resolve_input_params(inputs.input_param, workflow_output)
        for variable in input_variables:
            if variable not in llm_input_params:
                raise ValueError(f"The variable {variable} is not found in the input params.")
            prompt = prompt.replace('{{' + variable + '}}', llm_input_params[variable])

        messages = [{'role': 'user', 'content': prompt}]
        llm_output: LLMOutput = llm.call(messages=messages)

        # handle output parameters
        output_params: List[NodeOutputParams] = self._data.outputs
        output_params[0].value = llm_output.text
        workflow_output.workflow_parameters[self.id] = output_params

        return NodeOutput(node_id=self.id, status=NodeStatusEnum.SUCCEEDED, result=output_params)

