# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/13 10:42
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: planner.py
"""Base class for Planner."""
from abc import abstractmethod
import copy
import logging
from typing import Optional, List

from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.chat_memory import ChatMemory
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.memory.memory_manager import MemoryManager
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.configers.planner_configer import PlannerConfiger
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.base.util.memory_util import generate_messages

logging.getLogger().setLevel(logging.ERROR)


class Planner(ComponentBase):
    """
    Base class for all planners.

    All planners should inherit from this class
    """
    name: Optional[str] = None
    description: Optional[str] = None
    output_key: str = 'output'
    input_key: str = 'input'
    prompt_assemble_order: list = ['introduction', 'target', 'instruction']

    def __init__(self):
        """Initialize the ComponentBase."""
        super().__init__(component_type=ComponentEnum.PLANNER)

    @abstractmethod
    def invoke(self, agent_model: AgentModel, planner_input: dict,
               input_object: InputObject) -> dict:
        """Invoke the planner.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
            input_object (InputObject): The input parameters passed by the user.
        Returns:
            dict: The planner result.
        """
        pass

    def handle_memory(self, agent_model: AgentModel, planner_input: dict) -> ChatMemory | None:
        """Memory module processing.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
        Returns:
             Memory: The memory.
        """
        chat_history: list = planner_input.get('chat_history')
        memory_name = agent_model.memory.get('name')
        llm_model = agent_model.memory.get('llm_model') or dict()
        llm_name = llm_model.get('name') or agent_model.profile.get('llm_model').get('name')

        messages: list[Message] = generate_messages(chat_history)
        llm: LLM = LLMManager().get_instance_obj(llm_name)
        params: dict = dict()
        params['messages'] = messages
        params['llm'] = llm
        params['input_key'] = self.input_key
        params['output_key'] = self.output_key

        memory: ChatMemory = MemoryManager().get_instance_obj(component_instance_name=memory_name, new_instance=True)
        if memory is None:
            return None
        memory.set_by_agent_model(**params)
        return memory

    def run_all_actions(self, agent_model: AgentModel, planner_input: dict, input_object: InputObject):
        """Tool and knowledge processing.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
            input_object (InputObject): Agent input object.
        """
        action: dict = agent_model.action or dict()
        tools: list = action.get('tool') or list()
        knowledge: list = action.get('knowledge') or list()

        action_result: list = list()

        for tool_name in tools:
            tool = ToolManager().get_instance_obj(tool_name)
            if tool is None:
                continue
            tool_input = {key: input_object.get_data(key) for key in tool.input_keys}
            action_result.append(tool.run(**tool_input))

        for knowledge_name in knowledge:
            knowledge: Knowledge = KnowledgeManager().get_instance_obj(knowledge_name)
            if knowledge is None:
                continue
            knowledge_res: List[Document] = knowledge.store.query(
                Query(query_str=input_object.get_data(self.input_key), similarity_top_k=2), **input_object.to_dict())
            for document in knowledge_res:
                action_result.append(document.text)

        planner_input['background'] = planner_input['background'] or '' + "\n".join(action_result)

    def handle_prompt(self, agent_model: AgentModel, planner_input: dict):
        """Prompt module processing.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
        Returns:
            Prompt: The prompt instance.
        """
        pass

    def handle_llm(self, agent_model: AgentModel) -> LLM:
        """Language model module processing.

        Args:
            agent_model (AgentModel): Agent model object.
        Returns:
            LLM: The language model.
        """
        llm_name = agent_model.profile.get('llm_model').get('name')
        llm: LLM = LLMManager().get_instance_obj(component_instance_name=llm_name, new_instance=True)
        llm.set_by_agent_model(**agent_model.profile.get('llm_model'))
        return llm

    def initialize_by_component_configer(self, component_configer: PlannerConfiger) -> 'Planner':
        """Initialize the planner by the PlannerConfiger object.

        Args:
            component_configer(PlannerConfiger): the PlannerConfiger object
        Returns:
            Planner: the planner object
        """
        self.name = component_configer.name
        self.description = component_configer.description
        self.input_key = component_configer.input_key or self.input_key
        self.output_key = component_configer.output_key or self.output_key
        return self
