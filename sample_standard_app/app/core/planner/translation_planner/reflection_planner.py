# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/25 16:33
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: translation_planner.py

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager

from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.base.util.logging.logging_util import LOGGER


class ReflectionPlanner(Planner):

    def invoke(self, agent_model: AgentModel, planner_input: dict, input_object: InputObject) -> dict:
        work_agent = agent_model.plan.get('work_agent')
        reflection_agent = agent_model.plan.get('reflection_agent')
        improve_agent = agent_model.plan.get('improve_agent')

        work_agent = input_object.get_data('work_agent', work_agent)
        reflection_agent = input_object.get_data('reflection_agent', reflection_agent)
        improve_agent = input_object.get_data('improve_agent', improve_agent)

        init_agent_result = self.execute_agent(work_agent, planner_input)
        LOGGER.info(f"init_agent_result: {init_agent_result.to_json_str()}")

        planner_input['init_agent_result'] = init_agent_result.get_data('output')

        reflection_result = self.execute_agent(reflection_agent, planner_input)
        LOGGER.info(f"reflection_result: {reflection_result.to_json_str()}")

        planner_input['reflection_agent_result'] = reflection_result.get_data('output')

        improve_result = self.execute_agent(improve_agent, planner_input)
        LOGGER.info(f"improve_agent_result: {improve_result.to_json_str()}")

        return improve_result.to_dict()

    @staticmethod
    def execute_agent(agent_name: str, agent_input: dict):
        agent: Agent = AgentManager().get_instance_obj(agent_name)
        result = agent.run(**agent_input)
        return result
