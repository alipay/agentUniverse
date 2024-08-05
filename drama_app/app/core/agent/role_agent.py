# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/6 22:05
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: participant_agent.py
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.agent.plan.planner.planner_manager import PlannerManager
from agentuniverse.base.annotation.trace import trace_agent
from agentuniverse.base.util.logging.logging_util import LOGGER


class role_agent(Agent):
    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        agent_input['chat_history'] = input_object.get_data('chat_history')
        agent_input['background'] = input_object.get_data('background')
        agent_input['agent_name'] = input_object.get_data('agent_name')
        agent_input['total_round'] = input_object.get_data('total_round')
        agent_input['cur_round'] = input_object.get_data('cur_round')
        agent_input['roles'] = input_object.get_data('roles')
        agent_input['role'] = input_object.get_data('role')
        agent_input['type'] = 'chat'
        agent_input['action'] = input_object.get_data('action')

        keys = list(agent_input.keys())
        LOGGER.debug(f"role_agent keys {keys}")
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        return planner_result

    @trace_agent
    def run(self, **kwargs) -> OutputObject:
        """Agent instance running entry.

        Returns:
            OutputObject: Agent execution result
        """
        self.input_check(kwargs)
        input_object = InputObject(kwargs)

        agent_input = self.pre_parse_input(input_object)
        LOGGER.debug(f"agent_input {agent_input}")
        planner_result = self.execute(input_object, agent_input)

        LOGGER.debug(f"planner_result {planner_result}")
        agent_result = self.parse_result(planner_result)
        # print(agent_result)

        self.output_check(agent_result)
        output_object = OutputObject(agent_result)
        return output_object

    def execute(self, input_object: InputObject, agent_input: dict) -> dict:
        """Execute agent instance.

        Args:
            input_object (InputObject): input parameters passed by the user.
            agent_input (dict): agent input parsed from `input_object` by the user.

        Returns:
            dict: planner result generated by the planner execution.
        """
        LOGGER.debug(f"input_object {input_object}")
        LOGGER.debug(f"agent_input {agent_input}")

        if self.agent_model is None:
            raise Exception("代理模型未初始化")
        LOGGER.debug(f"planner name {self.agent_model.plan.get('planner').get('name')}")
        planner_base: Planner = PlannerManager().get_instance_obj(self.agent_model.plan.get('planner').get('name'))
        planner_result = planner_base.invoke(self.agent_model, agent_input, input_object)
        LOGGER.debug(f"role planner_result {planner_result}")
        return planner_result
