#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/6 22:05
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: host_agent.py

from datetime import datetime

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.agent.plan.planner.planner_manager import PlannerManager
from agentuniverse.base.annotation.trace import trace_agent
from agentuniverse.base.util.logging.logging_util import LOGGER


class law_drama_agent(Agent):

    def input_keys(self) -> list[str]:
        """返回代理的输入键。"""
        return ['input']

    def output_keys(self) -> list[str]:
        """返回代理的输出键。"""
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """解析代理的输入参数。

        参数:
            input_object(InputObject): 用户传递的输入参数。
            agent_input(dict): 代理预解析的输入参数。

        返回:
            dict: 由用户传递的 `input_object` 解析的代理输入参数。
        """
        agent_input['input'] = input_object.get_data('input')
        agent_input['roles'] = input_object.get_data('roles')
        agent_input['total_round'] = input_object.get_data('total_round')
        agent_input['current_round'] = input_object.get_data('current_round')
        agent_input['role'] = input_object.get_data('user_role')
        agent_input['cur_node'] = input_object.get_data('cur_node')
        agent_input['next_node'] = input_object.get_data('next_node')
        agent_input['drama'] = input_object.get_data('drama')
        # agent_input['user_role'] = input_object.get_data('user_role')

        LOGGER.debug(f"当前轮次 {agent_input}")

        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        """解析计划器的结果。

        参数:
            planner_result(dict): 计划器结果。

        返回:
            dict: 代理结果对象。
        """
        return planner_result

    def pre_parse_input(self, input_object) -> dict:
        """Agent execution parameter pre-parsing.

        Args:
            input_object (InputObject): input parameters passed by the user.
        Returns:
            dict: agent input preparsed by the agent.
        """
        agent_input = dict()
        agent_input['chat_history'] = input_object.get_data('chat_history') or []
        agent_input['background'] = input_object.get_data('background') or ''
        agent_input['image_urls'] = input_object.get_data('image_urls') or []
        agent_input['date'] = datetime.now().strftime('%Y-%m-%d')
        # agent_input['event'] = input_object.get_data('event') or EventDispatcher()

        self.parse_input(input_object, agent_input)

        keys = list(agent_input.keys())
        LOGGER.debug(f"court_host_agent keys {keys}")
        return agent_input

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

        # for planner_result in planner_results:

        LOGGER.debug(f"planner_result {planner_result}")
        agent_result = self.parse_result(planner_result)
        # print(agent_result)
        LOGGER.debug(f"agent_result {type(agent_result)} {agent_result}")
        self.output_check(agent_result)
        output_object = OutputObject(agent_result)
        # yield output_object
        return output_object

    def output_check(self, kwargs: dict):
        """Agent result check."""
        if not isinstance(kwargs, dict):
            raise Exception('Output type must be dict.')
        for key in self.output_keys():
            if key not in kwargs.keys():
                raise Exception(f'Output must have key: {key}.')

    def execute(self, input_object: InputObject, agent_input: dict) -> dict:
        """执行代理实例。

        参数:
            input_object (InputObject): 用户传递的输入参数。
            agent_input (dict): 由 `input_object` 解析的代理输入参数。

        返回:
            dict: 由计划器执行生成的计划器结果。
        """
        LOGGER.debug(f"执行 input_object {input_object}")
        LOGGER.debug(f"执行 agent_input {agent_input}")

        if self.agent_model is None:
            raise Exception("代理模型未初始化")
        LOGGER.debug(f"计划器名称 {self.agent_model.plan.get('planner').get('name')}")
        planner_base: Planner = PlannerManager().get_instance_obj(self.agent_model.plan.get('planner').get('name'))

        planner_result = planner_base.invoke(self.agent_model, agent_input, input_object)
        LOGGER.debug(f"planner_result {planner_result}")
        # for re in planner_result:
        #     LOGGER.debug(f"法庭 planner_result {re}")

        return planner_result
