# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/20 20:02
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: llm_node.py

from agentuniverse.prompt.prompt_model import AgentPromptModel
from agentuniverse.workflow.node.enum import NodeEnum
from agentuniverse.workflow.node.node import NodeData, Node
from agentuniverse.workflow.workflow_config import LLMConfig


class LLMNodeData(NodeData):
    model: LLMConfig
    prompt_template: AgentPromptModel


class LLMNode(Node):
    """The basic class of the llm node."""
    _data_cls = LLMNodeData

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = NodeEnum.LLM
