#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time   : 2024/6/22 15:05
# @Author : fluchw
# @Email  : zerozed00@qq.com
# @File   ：question_classification_agent.py
from langchain_core.utils.json import parse_json_markdown

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject

class QuestionClassificationAgent(Agent):
    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        print(planner_result)
        output = planner_result.get('output')
        output = parse_json_markdown(output)
        print(output)
        # planner_result['framework'] = output['framework']
        # planner_result['framework'] = output['framework']
        # planner_result['thought'] = output['thought']
        return planner_result
