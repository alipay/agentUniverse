# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/20 20:02
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: knowledge_node.py
from typing import List

from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager
from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.node import Node, NodeData
from agentuniverse.workflow.node.node_config import KnowledgeNodeInputParams, NodeInfoParams, NodeOutputParams
from agentuniverse.workflow.node.node_output import NodeOutput
from agentuniverse.workflow.workflow_output import WorkflowOutput


class KnowledgeNodeData(NodeData):
    inputs: KnowledgeNodeInputParams


class KnowledgeNode(Node):
    """The basic class of the knowledge node."""

    _data_cls = KnowledgeNodeData

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = NodeEnum.KNOWLEDGE

    def _run(self, workflow_output: WorkflowOutput) -> NodeOutput:
        inputs: KnowledgeNodeInputParams = self._data.inputs
        knowledge_params: List[NodeInfoParams] = inputs.knowledge_param

        param_dict = {param.name: str(param.value) for param in knowledge_params}
        knowledge_id = param_dict.get('id')
        query_top_k = param_dict.get('top_k')

        knowledge: Knowledge = KnowledgeManager().get_instance_obj(knowledge_id)
        if knowledge is None:
            raise ValueError("No knowledge with id {} was found.".format(knowledge_id))

        knowledge_input_params = {}
        if query_top_k:
            knowledge_input_params['similarity_top_k'] = query_top_k

        knowledge_input_params = self._resolve_input_params(inputs.input_param, workflow_output)

        document_texts = [document.text for document in knowledge.query_knowledge(**knowledge_input_params)]
        knowledge_res = '\n'.join(document_texts)
        output_params: List[NodeOutputParams] = self._data.outputs
        output_params[0].value = knowledge_res

        workflow_output.workflow_parameters[self.id] = output_params
        return NodeOutput(node_id=self.id, status=NodeStatusEnum.SUCCEEDED, result=output_params)
