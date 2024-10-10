# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/18 10:42
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: executing_planner.py
"""Execution planner module."""
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.plan.planner.planner import Planner

class DOEPlanner(Planner):
    """Executing planner class."""

    def invoke(self, agent_model: AgentModel, planner_input: dict, input_object: InputObject) -> dict:
        """Invoke the planner.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
            input_object (InputObject): The input parameters passed by the user.
        Returns:
            dict: The planner result.
        """

        data_fining_agent = agent_model.plan.get('planner').get('data_fining_agent')
        opinion_inject_agent = agent_model.plan.get('planner').get('opinion_inject_agent')
        expressing_agent = agent_model.plan.get('planner').get('expressing_agent')

        # 数据加工
        data_fining_output = AgentManager().get_instance_obj(data_fining_agent).run(**planner_input)
        self.stream_output(input_object, data_fining_output.to_dict())
        planner_input.update(data_fining_output.to_dict())

        # 观点注入
        opinion_inject_output = AgentManager().get_instance_obj(opinion_inject_agent).run(**planner_input)
        self.stream_output(input_object, opinion_inject_output.to_dict())
        planner_input.update(opinion_inject_output.to_dict())

        # 表达
        expressing_agent_result = AgentManager().get_instance_obj(expressing_agent).run(**planner_input)
        self.stream_output(input_object, expressing_agent_result.to_dict())

        return expressing_agent.dict()
