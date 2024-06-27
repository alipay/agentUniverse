# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/25 16:56
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: translation_planner.py

import copy
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.agent.plan.planner.planner_manager import PlannerManager

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject


class TranslationAgent(Agent):
    def input_keys(self) -> list[str]:
        return self.agent_model.profile.get('input_keys')

    def output_keys(self) -> list[str]:
        return self.agent_model.profile.get('output_keys')

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        for key in input_object.to_dict():
            agent_input[key] = input_object.get_data(key)
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        return planner_result

    def execute(self, input_object: InputObject, agent_input: dict) -> dict:
        planner_base: Planner = PlannerManager().get_instance_obj(self.agent_model.plan.get('planner').get('name'))
        agent_model = copy.deepcopy(self.agent_model)
        translation_type = input_object.get_data('execute_type')
        if translation_type == "multi":
            agent_model.profile['prompt_version'] = translation_type + "_" + agent_model.profile['prompt_version']
        planner_result = planner_base.invoke(agent_model, agent_input, input_object)
        return planner_result
