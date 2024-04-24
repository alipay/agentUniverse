# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/20 10:54
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: demo_peer_agent.py
from datetime import datetime

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject


class DemoPeerAgent(Agent):
    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, planner_input: dict) -> dict:
        planner_input['input'] = input_object.get_data('input')
        return planner_input

    def parse_result(self, planner_result: dict) -> dict:
        return {"output": planner_result.get('result')[0].get('expressing_result').get_data('output')}
