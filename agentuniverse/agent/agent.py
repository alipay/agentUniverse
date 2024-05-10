# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/12 19:36
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: agent.py
"""The definition of agent paradigm."""
from abc import abstractmethod
from datetime import datetime
from typing import Optional

from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.agent.plan.planner.planner_manager import PlannerManager
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager \
    import ApplicationConfigManager
from agentuniverse.base.config.component_configer.configers.agent_configer \
    import AgentConfiger
from agentuniverse.llm.llm import LLM


class Agent(ComponentBase):
    """The parent class of all agent models, containing only attributes."""

    agent_model: Optional[AgentModel] = None

    def __init__(self):
        """Initialize the AgentModel with the given keyword arguments."""
        super().__init__(component_type=ComponentEnum.AGENT)

    @abstractmethod
    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        pass

    @abstractmethod
    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        pass

    @abstractmethod
    def parse_input(self, input_object: InputObject, planner_input: dict) -> dict:
        """Planner parameter parsing.

        Args:
            input_object(InputObject): agent parameter object
            planner_input(dict): Planner input
        Returns:
            dict: Planner parameter.
        """
        pass

    @abstractmethod
    def parse_result(self, planner_result: dict) -> dict:
        """Planner result parser.

        Args:
            planner_result(dict): Planner result
        Returns:
            dict: Agent result object.
        """
        pass

    def run(self, **kwargs) -> OutputObject:
        """Agent instance running entry.

        Returns:
            OutputObject: Agent execution result
        """
        self.input_check(kwargs)
        input_object = InputObject(kwargs)
        execute_result = self.execute(input_object)
        self.output_check(execute_result)
        output_object = OutputObject(execute_result)
        return output_object

    def execute(self, input_object: InputObject) -> dict:
        """Execute agent instance.

        Args:
            input_object(InputObject): agent parameter object
        Returns:
            dict: Agent result object.
        """
        planner_input = self.pre_parse_input(input_object)

        planner_base: Planner = PlannerManager().get_instance_obj(self.agent_model.plan.get('planner').get('name'))
        planner_result = planner_base.invoke(self.agent_model, planner_input, input_object)

        parser_result = self.parse_result(planner_result)
        return parser_result

    def pre_parse_input(self, input_object) -> dict:
        """Agent execution parameter pre-parsing.

        Args: input_object(InputObject): agent parameter object
        Returns:
            dict: Planner input
        """
        planner_input = dict()
        planner_input['chat_history'] = input_object.get_data('chat_history') or ''
        planner_input['background'] = input_object.get_data('background') or ''
        planner_input['date'] = datetime.now().strftime('%Y-%m-%d')

        self.parse_input(input_object, planner_input)
        return planner_input

    def get_instance_code(self) -> str:
        """Return the full name of the agent."""
        appname = ApplicationConfigManager().app_configer.base_info_appname
        name = self.agent_model.info.get('name')
        return (f'{appname}.'
                f'{self.component_type.value.lower()}.{name}')

    def input_check(self, kwargs: dict):
        """Agent parameter check."""
        for key in self.input_keys():
            if key not in kwargs.keys():
                raise Exception(f'Input must have key: {key}.')

    def output_check(self, kwargs: dict):
        """Agent result check."""
        if not isinstance(kwargs, dict):
            raise Exception('Output type must be dict.')
        for key in self.output_keys():
            if key not in kwargs.keys():
                raise Exception(f'Output must have key: {key}.')

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'Agent':
        """Initialize the LLM by the ComponentConfiger object.

        Args:
            component_configer(LLMConfiger): the ComponentConfiger object
        Returns:
            LLM: the LLM object
        """
        agent_config: Optional[AgentConfiger] = component_configer.load()
        info: Optional[dict] = agent_config.info
        profile: Optional[dict] = agent_config.profile
        plan: Optional[dict] = agent_config.plan
        memory: Optional[dict] = agent_config.memory
        action: Optional[dict] = agent_config.action
        agent_model: Optional[AgentModel] = AgentModel(info=info, profile=profile,
                                                       plan=plan, memory=memory, action=action)
        self.agent_model = agent_model
        return self
