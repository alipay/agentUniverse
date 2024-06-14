# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/6 22:05
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: participant_agent.py
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject


class ParticipantAgent(Agent):
    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        agent_input['agent_name'] = input_object.get_data('agent_name')
        agent_input['total_round'] = input_object.get_data('total_round')
        agent_input['cur_round'] = input_object.get_data('cur_round')
        agent_input['participants'] = input_object.get_data('participants')
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        return planner_result
