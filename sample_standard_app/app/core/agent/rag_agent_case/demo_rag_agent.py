# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/2 19:56
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: demo_rag_agent.py
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject


class DemoRagAgent(Agent):
    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, planner_input: dict) -> dict:
        input = input_object.get_data('input')
        planner_input['input'] = input
        return planner_input

    def parse_result(self, planner_result: dict) -> dict:
        return planner_result
